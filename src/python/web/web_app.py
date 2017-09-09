# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from threading import Thread
from queue import Queue, Empty
import os
from typing import Optional

# 3rd party libs
import bottle
from bottle import static_file
from paste import httpserver
from paste.translogger import TransLogger

# my libs
from common import overrides, PylftpJob, PylftpContext
from controller import Controller
from .serialize import Serialize
from model import IModelListener, ModelFile


_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class WebAppJob(PylftpJob):
    """
    Web interface service 
    :return: 
    """
    def __init__(self, context: PylftpContext, controller: Controller):
        super().__init__(name=self.__class__.__name__, context=context)
        self.web_access_logger = context.web_access_logger
        self.__context = context
        self.__controller = controller
        self.__app = None
        self.__server = None
        self.__server_thread = None

    @overrides(PylftpJob)
    def setup(self):
        self.__app = WebApp(self.logger, self.__controller)
        # Note: do not use requestlogger.WSGILogger as it breaks SSE
        self.__server = MyWSGIRefServer(self.web_access_logger,
                                        host="localhost",
                                        port=self.__context.config.web.port)
        self.__server_thread = Thread(target=bottle.run,
                                      kwargs={
                                          'app': self.__app,
                                          'server': self.__server
                                      })
        self.__server_thread.start()

    @overrides(PylftpJob)
    def execute(self):
        pass

    @overrides(PylftpJob)
    def cleanup(self):
        self.__app.stop()
        self.__server.stop()
        self.__server_thread.join()


class WebResponseModelListener(IModelListener):
    """
    Model listener used by Web app to listen to model updates
    One listener should be created for each new request
    This listener queues notifications in an event queue
    so that they can be processed in the web thread (and quickly
    free up the controller thread)
    """
    def __init__(self):
        self.__queue = Queue()

    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        self.__queue.put(Serialize.UpdateEvent(change=Serialize.UpdateEvent.Change.ADDED,
                                               old_file=None,
                                               new_file=file))

    @overrides(IModelListener)
    def file_removed(self, file: ModelFile):
        self.__queue.put(Serialize.UpdateEvent(change=Serialize.UpdateEvent.Change.REMOVED,
                                               old_file=file,
                                               new_file=None))

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        self.__queue.put(Serialize.UpdateEvent(change=Serialize.UpdateEvent.Change.UPDATED,
                                               old_file=old_file,
                                               new_file=new_file))

    def get_next_event(self, timeout_in_ms: int) -> Optional[Serialize.UpdateEvent]:
        """
        Returns the next event, or blocks for the specified timeout until an event is available.
        Returns None if timeout expires and no event is available
        :return:
        """
        try:
            return self.__queue.get(block=True, timeout=float(timeout_in_ms)/1000)
        except Empty:
            return None


class WebApp(bottle.Bottle):
    """
    Web app implementation
    """
    _EVENT_BLOCK_INTERVAL_IN_MS = 500

    def __init__(self, logger: logging.Logger, controller: Controller):
        super().__init__()
        self.logger = logger.getChild("WebApp")
        self.__controller = controller
        self.__stop = False
        self.get("/stream")(self.stream)
        self.route("/")(self.index)
        self.route("/<file_path:path>")(self.static)

    def stop(self):
        """
        Exit gracefully, kill any connections and clean up any state
        :return: 
        """
        self.__stop = True

    def index(self):
        return self.static("index.html")

    # noinspection PyMethodMayBeStatic
    def static(self, file_path: str):
        return static_file(file_path, root=os.path.join(_DIR_PATH, "..", "..", "html"))

    def stream(self) -> str:
        model_listener = None
        try:
            # Setup the response header
            bottle.response.content_type = "text/event-stream"
            bottle.response.cache_control = "no-cache"

            serialize = Serialize()
            model_listener = WebResponseModelListener()

            initial_model_files = self.__controller.get_model_files_and_add_listener(model_listener)

            # Send the initial model
            yield serialize.model(initial_model_files)

            # Send the model update event until the connection closes
            while not self.__stop:
                event = model_listener.get_next_event(timeout_in_ms=WebApp._EVENT_BLOCK_INTERVAL_IN_MS)
                if event:
                    yield serialize.update_event(event)
                else:
                    # need to yield a newline, otherwise the finally block
                    # is not called upon connection exit
                    yield "\n"

        finally:
            if self.__stop:
                self.logger.debug("Stream connection stopped by server")
            else:
                self.logger.debug("Stream connection stopped by client")

            # Cleanup
            if model_listener:
                self.__controller.remove_model_listener(model_listener)


class MyWSGIHandler(httpserver.WSGIHandler):
    """
    This class is overridden to fix a bug in Paste http server
    """
    # noinspection SpellCheckingInspection
    def wsgi_write_chunk(self, chunk):
        if type(chunk) is str:
            chunk = str.encode(chunk)
        super().wsgi_write_chunk(chunk)


class MyWSGIRefServer(bottle.ServerAdapter):
    """
    Extend bottle's default server to support programatic stopping of server
    Copied from: https://stackoverflow.com/a/16056443
    """
    quiet = True  # disable logging to stdout

    def __init__(self, logger: logging.Logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.server = None

    @overrides(bottle.ServerAdapter)
    def run(self, handler):
        handler = TransLogger(handler, logger=self.logger, setup_console_handler=(not self.quiet))
        self.server = httpserver.serve(handler, host=self.host, port=str(self.port), start_loop=False,
                                       handler=MyWSGIHandler,
                                       **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()
