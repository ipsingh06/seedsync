# Copyright 2017, Inderpreet Singh, All rights reserved.

import time
import logging
from threading import Thread

# 3rd party libs
import bottle
from paste import httpserver
from paste.translogger import TransLogger

# my libs
from common import overrides, PylftpJob, PylftpContext


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

    @overrides(PylftpJob)
    def setup(self):
        self.app = WebApp(self.logger)
        # Note: do not use requestlogger.WSGILogger as it breaks SSE

        # TODO: grab from config
        self.server = MyWSGIRefServer(self.web_access_logger, host="localhost", port=8080)
        self.server_thread = Thread(target=bottle.run,
                                    kwargs={
                                        'app': self.app,
                                        'server': self.server
                                    })
        self.server_thread.start()

    @overrides(PylftpJob)
    def execute(self):
        pass

    @overrides(PylftpJob)
    def cleanup(self):
        self.app.stop()
        self.server.stop()
        self.server_thread.join()


sse_test_page = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/1.8.3/jquery.min.js "></script>
        <script>
            $(document).ready(function() {
                console.log("Ready...")
                var es = new EventSource("stream");
                es.onerror = function (e) {
                    console.log("Error!");
                };
                es.onopen = function (e) {
                    console.log("Opened!");
                };
                es.onclose = function (e) {
                    console.log("Closed!");
                };
                es.onmessage = function (e) {
                    $("#log").html($("#log").html()
                        + "<p>Event: " + e.event + ", data: " + e.data + "</p>");
                };
            })
        </script>
    </head>
    <body>
        <div id="log" style="font-family: courier; font-size: 0.75em;"></div>
    </body>
</html>
"""


class WebApp(bottle.Bottle):
    """
    Web app implementation
    """
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger.getChild("WebApp")
        self.__stop = False
        self.get("/")(self.index)
        self.get("/stream")(self.stream)

    def stop(self):
        """
        Exit gracefully, kill any connections and clean up any state
        :return: 
        """
        self.__stop = True

    @staticmethod
    def _sse_pack(d):
        """Pack data in SSE format"""
        buffer = ''
        for k in ['retry', 'id', 'event', 'data']:
            if k in d.keys():
                buffer += '%s: %s\n' % (k, d[k])
        return buffer + '\n'

    def index(self) -> str:
        return sse_test_page

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
                                       **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()
