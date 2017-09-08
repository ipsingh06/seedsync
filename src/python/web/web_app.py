# Copyright 2017, Inderpreet Singh, All rights reserved.

import time
import logging
from threading import Thread
import os

# 3rd party libs
import bottle
from bottle import static_file
from paste import httpserver
from paste.translogger import TransLogger

# my libs
from common import overrides, PylftpJob, PylftpContext
from controller import Controller


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
        self.__app = WebApp(self.logger)
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


class WebApp(bottle.Bottle):
    """
    Web app implementation
    """
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger.getChild("WebApp")
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

    @staticmethod
    def _sse_pack(d):
        """Pack data in SSE format"""
        buffer = ''
        for k in ['retry', 'id', 'event', 'data']:
            if k in d.keys():
                buffer += '%s: %s\n' % (k, d[k])
        return buffer + '\n'

    def stream(self) -> str:
        # "Using server-sent events"
        # https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events
        # "Stream updates with server-sent events"
        # http://www.html5rocks.com/en/tutorials/eventsource/basics/
        bottle.response.content_type = 'text/event-stream'
        bottle.response.cache_control = 'no-cache'

        # Set client-side auto-reconnect timeout, ms.
        msg = {
            'retry': '2000'
        }
        msg.update({
            'event': 'init',
            'data': 'something',
            'id': 0
        })
        yield self._sse_pack(msg)

        n = 1

        # Keep connection alive no more then... (s)
        end = time.time() + 60
        while not self.__stop and time.time() < end:
            msg = {
                'id': n,
                'data': '%i' % n,
            }
            yield self._sse_pack(msg)
            n += 1
            time.sleep(1)
        if self.__stop:
            self.logger.debug("App connection stopped by server")


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
