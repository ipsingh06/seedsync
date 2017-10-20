# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from threading import Thread

import bottle
from paste import httpserver
from paste.translogger import TransLogger

from .web_app import WebApp
from common import overrides, PylftpJob, PylftpContext


class WebAppJob(PylftpJob):
    """
    Web interface service
    :return:
    """
    def __init__(self, context: PylftpContext, web_app: WebApp):
        super().__init__(name=self.__class__.__name__, context=context)
        self.web_access_logger = context.web_access_logger
        self.__context = context
        self.__app = web_app
        self.__server = None
        self.__server_thread = None

    @overrides(PylftpJob)
    def setup(self):
        # Note: do not use requestlogger.WSGILogger as it breaks SSE
        self.__server = MyWSGIRefServer(self.web_access_logger,
                                        host="0.0.0.0",
                                        port=self.__context.config.web.port)
        self.__server_thread = Thread(target=bottle.run,
                                      kwargs={
                                          'app': self.__app,
                                          'server': self.__server,
                                          'debug': self.__context.args.debug
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
