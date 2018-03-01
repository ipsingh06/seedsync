# Copyright 2017, Inderpreet Singh, All rights reserved.

from threading import Event
from urllib.parse import unquote

from bottle import HTTPResponse

from common import overrides
from controller import Controller
from ..web_app import IHandler, WebApp


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


class ControllerHandler(IHandler):
    def __init__(self, controller: Controller):
        self.__controller = controller

    @overrides(IHandler)
    def add_routes(self, web_app: WebApp):
        web_app.add_handler("/server/command/queue/<file_name>", self.__handle_action_queue)
        web_app.add_handler("/server/command/stop/<file_name>", self.__handle_action_stop)
        web_app.add_handler("/server/command/extract/<file_name>", self.__handle_action_extract)
        web_app.add_handler("/server/command/delete_local/<file_name>", self.__handle_action_delete_local)
        web_app.add_handler("/server/command/delete_remote/<file_name>", self.__handle_action_delete_remote)

    def __handle_action_queue(self, file_name: str):
        """
        Request a QUEUE action
        :param file_name:
        :return:
        """
        # value is double encoded
        file_name = unquote(file_name)

        command = Controller.Command(Controller.Command.Action.QUEUE, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Queued file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def __handle_action_stop(self, file_name: str):
        """
        Request a STOP action
        :param file_name:
        :return:
        """
        # value is double encoded
        file_name = unquote(file_name)

        command = Controller.Command(Controller.Command.Action.STOP, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Stopped file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def __handle_action_extract(self, file_name: str):
        """
        Request a EXTRACT action
        :param file_name:
        :return:
        """
        # value is double encoded
        file_name = unquote(file_name)

        command = Controller.Command(Controller.Command.Action.EXTRACT, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Requested extraction for file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def __handle_action_delete_local(self, file_name: str):
        """
        Request a DELETE LOCAL action
        :param file_name:
        :return:
        """
        # value is double encoded
        file_name = unquote(file_name)

        command = Controller.Command(Controller.Command.Action.DELETE_LOCAL, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Requested local delete for file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)

    def __handle_action_delete_remote(self, file_name: str):
        """
        Request a DELETE REMOTE action
        :param file_name:
        :return:
        """
        # value is double encoded
        file_name = unquote(file_name)

        command = Controller.Command(Controller.Command.Action.DELETE_REMOTE, file_name)
        callback = WebResponseActionCallback()
        command.add_callback(callback)
        self.__controller.queue_command(command)
        callback.wait()
        if callback.success:
            return HTTPResponse(body="Requested remote delete for file '{}'".format(file_name))
        else:
            return HTTPResponse(body=callback.error, status=400)
