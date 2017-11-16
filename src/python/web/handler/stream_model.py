# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import Optional

from ..web_app import IStreamHandler
from ..utils import StreamQueue
from ..serialize import SerializeModel
from model import IModelListener, ModelFile
from common import overrides
from controller import Controller


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


class ModelStreamHandler(IStreamHandler):
    _EVENT_BLOCK_INTERVAL_IN_MS = 500

    def __init__(self, controller: Controller):
        self.controller = controller
        self.serialize = SerializeModel()
        self.model_listener = WebResponseModelListener()
        self.initial_model_files = None
        self.first_run = True

    @staticmethod
    @overrides(IStreamHandler)
    def get_path() -> str:
        return "/server/model-stream"

    @overrides(IStreamHandler)
    def setup(self):
        self.initial_model_files = self.controller.get_model_files_and_add_listener(self.model_listener)

    @overrides(IStreamHandler)
    def get_value(self) -> Optional[str]:
        if self.first_run:
            self.first_run = False
            return self.serialize.model(self.initial_model_files)
        else:
            event = self.model_listener.get_next_event(timeout_in_ms=ModelStreamHandler._EVENT_BLOCK_INTERVAL_IN_MS)
            if event:
                return self.serialize.update_event(event)
            else:
                return None

    @overrides(IStreamHandler)
    def cleanup(self):
        if self.model_listener:
            self.controller.remove_model_listener(self.model_listener)
