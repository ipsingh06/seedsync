# Copyright 2017, Inderpreet Singh, All rights reserved.

from threading import Thread

# 3rd party libs
import bottle
from requestlogger import WSGILogger, ApacheFormatter

# my libs
from common import PylftpJob, PylftpContext


class WebAppJob(PylftpJob):
    """
    Web interface service 
    :return: 
    """
    def __init__(self, context: PylftpContext):
        super().__init__(name=self.__class__.__name__, context=context)
        self.web_access_logger = context.web_access_logger
        self.app = None
        self.server = None
        self.server_thread = None

    def setup(self):
        self.app = WebApp()
        self.app = WSGILogger(self.app, self.web_access_logger.handlers, ApacheFormatter())

        self.server = MyWSGIRefServer(host="localhost", port=88)
        self.server_thread = Thread(target=bottle.run,
                                    kwargs={
                                        'app': self.app,
                                        'server': self.server
                                    })
        self.server_thread.start()

    def execute(self):
        pass

    def cleanup(self):
        self.server.stop()
        self.server_thread.join()


class WebApp(bottle.Bottle):
    """
    Web app implementation
    """
    def __init__(self):
        super().__init__()
        self.data = None
        self.route("/")(self.index)

    def index(self) -> str:
        self.data = None
        return "Hello World"


class MyWSGIRefServer(bottle.ServerAdapter):
    """
    Extend bottle's default server to support programatic stopping of server
    Copied from: https://stackoverflow.com/a/16056443
    """
    server = None
    quiet = True  # disable logging to stdout

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def __init__(self, request, client_address, server):
                    super().__init__(request, client_address, server)

                def log_request(*args, **kw):
                    pass

            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()
