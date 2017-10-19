# Copyright 2017, Inderpreet Singh, All rights reserved.

from threading import Event

import bottle
from bottle import static_file, HTTPResponse

from .status import BackendStatus
from .serialize import SerializeModel, SerializeBackendStatus
from .utils import StreamQueue
from common import overrides, PylftpContext
from controller import Controller
from model import IModelListener, ModelFile


class BackendStatusListener(StreamQueue[BackendStatus]):
    """
    Status listener used by status streams to listen to status updates
    One listener should be created for each new request
    """
    def __init__(self):
        super().__init__()

    def notify(self, status: BackendStatus):
        self.put(status)


class WebResponseModelListener(IModelListener, StreamQueue[SerializeModel.UpdateEvent]):
    """
    Model listener used by streams to listen to model updates
    One listener should be created for each new request
    """
    def __init__(self):
        super().__init__()

    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        self.put(SerializeModel.UpdateEvent(change=SerializeModel.UpdateEvent.Change.ADDED,
                                            old_file=None,
                                            new_file=file))

    @overrides(IModelListener)
    def file_removed(self, file: ModelFile):
        self.put(SerializeModel.UpdateEvent(change=SerializeModel.UpdateEvent.Change.REMOVED,
                                            old_file=file,
                                            new_file=None))

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        self.put(SerializeModel.UpdateEvent(change=SerializeModel.UpdateEvent.Change.UPDATED,
                                            old_file=old_file,
                                            new_file=new_file))


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
    _EVENT_BLOCK_INTERVAL_IN_MS = 500

    def __init__(self, context: PylftpContext, controller: Controller):
        super().__init__()
        self.logger = context.logger.getChild("WebApp")
        self.__controller = controller
        self.__html_path = context.args.html_path
        self.logger.info("Html path set to: {}".format(self.__html_path))
        self.__stop = False
        self.__status = BackendStatus(up=True, error_msg=None)
        self.__status_listeners = []

        # Routes
        self.get("/stream")(self.stream)
        self.get("/status")(self.status)
        self.get("/queue/<file_name>")(self.action_queue)
        self.get("/stop/<file_name>")(self.action_stop)
        self.route("/")(self.index)
        self.route("/<file_path:path>")(self.static)

    def set_backend_status(self, status: BackendStatus):
        """
        Notify the web app about the backend status
        :param status:
        :return:
        """
        self.__status = status
        for listener in self.__status_listeners:
            listener.notify(status)

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

    # TODO: can we make the stream methods generic?? they both have a setup, loop and cleanup
    def status(self) -> str:
        """
        Streams backend status updates to client
        :return:
        """
        status_listener = None
        try:
            # Setup the response header
            bottle.response.content_type = "text/event-stream"
            bottle.response.cache_control = "no-cache"

            serialize = SerializeBackendStatus()
            status_listener = BackendStatusListener()
            self.__status_listeners.append(status_listener)

            yield serialize.status(self.__status)

            # Send the model update event until the connection closes
            while not self.__stop:
                status = status_listener.get_next_event(timeout_in_ms=WebApp._EVENT_BLOCK_INTERVAL_IN_MS)
                if status:
                    yield serialize.status(status)
                else:
                    # need to yield a newline, otherwise the finally block
                    # is not called upon connection exit
                    yield "\n"

        finally:
            if self.__stop:
                self.logger.debug("Status stream connection stopped by server")
            else:
                self.logger.debug("status stream connection stopped by client")

            # Cleanup
            if status_listener:
                self.__status_listeners.remove(status_listener)

    def stream(self) -> str:
        """
        Streams model updates to client
        See the Serialize class for api
        :return:
        """
        model_listener = None
        try:
            # Setup the response header
            bottle.response.content_type = "text/event-stream"
            bottle.response.cache_control = "no-cache"

            serialize = SerializeModel()
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
                self.logger.debug("Model stream connection stopped by server")
            else:
                self.logger.debug("Model stream connection stopped by client")

            # Cleanup
            if model_listener:
                self.__controller.remove_model_listener(model_listener)
