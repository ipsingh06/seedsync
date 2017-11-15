# Copyright 2017, Inderpreet Singh, All rights reserved.

import functools
from threading import Event
from typing import Type

import bottle
from bottle import static_file, HTTPResponse

from common import overrides, PylftpContext
from controller import Controller
from .web_app_stream import WebAppStream
from .stream_model import StreamModel
from .stream_status import StreamStatus


class WebResponseActionCallback(Controller.Command.ICallback):
    """
    Controller action callback used by model streams to wait for action
    status.
    Clients should call wait() method to wait for the status,
    then query the status from 'success' and 'error'
    """

    def __init__(self):
        self.__event = Event()
        self.success = None
        self.error = None

    @overrides(Controller.Command.ICallback)
    def on_failure(self, error: str):
        self.success = False
        self.error = error
        self.__event.set()

    @overrides(Controller.Command.ICallback)
    def on_success(self):
        self.success = True
        self.__event.set()

    def wait(self):
        self.__event.wait()


class WebApp(bottle.Bottle):
    """
    Web app implementation
    """
    def __init__(self, context: PylftpContext, controller: Controller):
        super().__init__()
        self.logger = context.logger.getChild("WebApp")
        self.__controller = controller
        self.__html_path = context.args.html_path
        self.__status = context.status
        self.logger.info("Html path set to: {}".format(self.__html_path))
        self.__stop = False
        self.__request_restart = False

        # Backend routes
        # Streaming routes
        self.get("/server/status-stream")(functools.partial(
            self.web_stream,
            cls=StreamStatus,
            status=self.__status
        ))
        self.get("/server/model-stream")(functools.partial(
            self.web_stream,
            cls=StreamModel,
            controller=controller
        ))
        # Non-streaming routes
        self.get("/server/command/restart")(self.action_restart)
        self.get("/server/command/queue/<file_name>")(self.action_queue)
        self.get("/server/command/stop/<file_name>")(self.action_stop)

        # Front-end routes
        self.route("/")(self.index)
        self.route("/dashboard")(self.index)
        self.route("/settings")(self.index)
        # For static files
        self.route("/<file_path:path>")(self.static)

    def process(self):
        """
        Advance the web app state
        :return:
        """
        pass

    def is_restart_requested(self):
        """
        Returns true is a restart is requested
        :return:
        """
        return self.__request_restart

    def stop(self):
        """
        Exit gracefully, kill any connections and clean up any state
        :return: 
        """
        self.__stop = True

    def index(self):
        """
        Serves the index.html static file
        :return:
        """
        return self.static("index.html")

    # noinspection PyMethodMayBeStatic
    def static(self, file_path: str):
        """
        Serves all the static files
        :param file_path:
        :return:
        """
        return static_file(file_path, root=self.__html_path)

    def action_restart(self):
        """
        Request a server restart
        :return:
        """
        self.logger.info("Received a restart action")
        self.__request_restart = True
        return HTTPResponse(body="Requested restart")

    def action_queue(self, file_name: str):
        """
        Request a QUEUE action
        :param file_name:
        :return:
        """
        command = Controller.Command(Controller.Command.Action.QUEUE, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Queued file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def action_stop(self, file_name: str):
        """
        Request a STOP action
        :param file_name:
        :return:
        """
        command = Controller.Command(Controller.Command.Action.STOP, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Stopped file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def web_stream(self, cls: Type[WebAppStream], **kwargs):
        stream = cls(**kwargs)
        try:
            # Setup the response header
            bottle.response.content_type = "text/event-stream"
            bottle.response.cache_control = "no-cache"

            # Setup the stream
            stream.setup()

            # Get streaming values until the connection closes
            while not self.__stop:
                value = stream.get_value()
                if value:
                    yield value
                else:
                    # need to yield a newline, otherwise the finally block
                    # is not called upon connection exit
                    yield "\n"

        finally:
            self.logger.debug("Stream '{}' connection stopped by {}".format(
                cls.__name__,
                "server" if self.__stop else "client"
            ))

            # Cleanup
            stream.cleanup()
