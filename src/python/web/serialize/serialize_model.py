# Copyright 2017, Inderpreet Singh, All rights reserved.

from enum import Enum
import json
from typing import List, Optional

from .serialize import Serialize
from model import ModelFile


class SerializeModel(Serialize):
    """
    This class defines the serialization interface between the python backend
    and the EventSource client frontend for the model stream.
    """

    class UpdateEvent:
        class Change(Enum):
            ADDED = 0
            REMOVED = 1
            UPDATED = 2

        def __init__(self, change: Change, old_file: Optional[ModelFile], new_file: Optional[ModelFile]):
            self.change = change
            self.old_file = old_file
            self.new_file = new_file

    # Event keys
    __EVENT_INIT = "model-init"
    __EVENT_UPDATE = {
        UpdateEvent.Change.ADDED: "model-added",
        UpdateEvent.Change.REMOVED: "model-removed",
        UpdateEvent.Change.UPDATED: "model-updated"
    }
    __KEY_UPDATE_OLD_FILE = "old_file"
    __KEY_UPDATE_NEW_FILE = "new_file"

    # Model file keys
    __KEY_FILE_NAME = "name"
    __KEY_FILE_IS_DIR = "is_dir"
    __KEY_FILE_STATE = "state"
    __VALUES_FILE_STATE = {
        ModelFile.State.DEFAULT: "default",
        ModelFile.State.QUEUED: "queued",
        ModelFile.State.DOWNLOADING: "downloading",
        ModelFile.State.DOWNLOADED: "downloaded",
        ModelFile.State.DELETED: "deleted",
        ModelFile.State.EXTRACTING: "extracting",
        ModelFile.State.EXTRACTED: "extracted"
    }
    __KEY_FILE_REMOTE_SIZE = "remote_size"
    __KEY_FILE_LOCAL_SIZE = "local_size"
    __KEY_FILE_DOWNLOADING_SPEED = "downloading_speed"
    __KEY_FILE_ETA = "eta"
    __KEY_FILE_IS_EXTRACTABLE = "is_extractable"
    __KEY_FILE_LOCAL_CREATED_TIMESTAMP = "local_created_timestamp"
    __KEY_FILE_LOCAL_MODIFIED_TIMESTAMP = "local_modified_timestamp"
    __KEY_FILE_REMOTE_CREATED_TIMESTAMP = "remote_created_timestamp"
    __KEY_FILE_REMOTE_MODIFIED_TIMESTAMP = "remote_modified_timestamp"
    __KEY_FILE_FULL_PATH = "full_path"
    __KEY_FILE_CHILDREN = "children"

    @staticmethod
    def __model_file_to_json_dict(model_file: ModelFile) -> dict:
        json_dict = dict()
        json_dict[SerializeModel.__KEY_FILE_NAME] = model_file.name
        json_dict[SerializeModel.__KEY_FILE_IS_DIR] = model_file.is_dir
        json_dict[SerializeModel.__KEY_FILE_STATE] = SerializeModel.__VALUES_FILE_STATE[model_file.state]
        json_dict[SerializeModel.__KEY_FILE_REMOTE_SIZE] = model_file.remote_size
        json_dict[SerializeModel.__KEY_FILE_LOCAL_SIZE] = model_file.local_size
        json_dict[SerializeModel.__KEY_FILE_DOWNLOADING_SPEED] = model_file.downloading_speed
        json_dict[SerializeModel.__KEY_FILE_ETA] = model_file.eta
        json_dict[SerializeModel.__KEY_FILE_IS_EXTRACTABLE] = model_file.is_extractable
        json_dict[SerializeModel.__KEY_FILE_LOCAL_CREATED_TIMESTAMP] = \
            str(model_file.local_created_timestamp.timestamp()) if model_file.local_created_timestamp else None
        json_dict[SerializeModel.__KEY_FILE_LOCAL_MODIFIED_TIMESTAMP] = \
            str(model_file.local_modified_timestamp.timestamp()) if model_file.local_modified_timestamp else None
        json_dict[SerializeModel.__KEY_FILE_REMOTE_CREATED_TIMESTAMP] = \
            str(model_file.remote_created_timestamp.timestamp()) if model_file.remote_created_timestamp else None
        json_dict[SerializeModel.__KEY_FILE_REMOTE_MODIFIED_TIMESTAMP] = \
            str(model_file.remote_modified_timestamp.timestamp()) if model_file.remote_modified_timestamp else None
        json_dict[SerializeModel.__KEY_FILE_FULL_PATH] = model_file.full_path
        json_dict[SerializeModel.__KEY_FILE_CHILDREN] = list()
        for child in model_file.get_children():
            json_dict[SerializeModel.__KEY_FILE_CHILDREN].append(SerializeModel.__model_file_to_json_dict(child))
        return json_dict

    def model(self, model_files: List[ModelFile]) -> str:
        """
        Serialize the model
        :return:
        """
        model_json_list = [SerializeModel.__model_file_to_json_dict(f) for f in model_files]
        model_json = json.dumps(model_json_list)
        return self._sse_pack(event=SerializeModel.__EVENT_INIT,
                              data=model_json)

    def update_event(self, event: UpdateEvent):
        model_file_json_dict = {
            SerializeModel.__KEY_UPDATE_OLD_FILE:
                SerializeModel.__model_file_to_json_dict(event.old_file) if event.old_file else None,
            SerializeModel.__KEY_UPDATE_NEW_FILE:
                SerializeModel.__model_file_to_json_dict(event.new_file) if event.new_file else None
        }
        model_file_json = json.dumps(model_file_json_dict)
        return self._sse_pack(event=SerializeModel.__EVENT_UPDATE[event.change],
                              data=model_file_json)
