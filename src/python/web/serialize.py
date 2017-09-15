# Copyright 2017, Inderpreet Singh, All rights reserved.

from enum import Enum
import json
from typing import List, Optional

# my libs
from model import ModelFile


class Serialize:
    """
    This class defines the serialization interface between the python backend
    and the EventSource client frontend.
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

    def __init__(self):
        self.id = -1

    # Event keys
    __EVENT_INIT = "init"
    __EVENT_UPDATE = {
        UpdateEvent.Change.ADDED: "added",
        UpdateEvent.Change.REMOVED: "removed",
        UpdateEvent.Change.UPDATED: "updated"
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
        ModelFile.State.DOWNLOADED: "downloaded"
    }
    __KEY_FILE_REMOTE_SIZE = "remote_size"
    __KEY_FILE_LOCAL_SIZE = "local_size"
    __KEY_FILE_DOWNLOADING_SPEED = "downloading_speed"
    __KEY_FILE_ETA = "eta"
    __KEY_FILE_FULL_PATH = "full_path"
    __KEY_FILE_CHILDREN = "children"

    @staticmethod
    def __sse_pack(idx: int, event: str, data: str) -> str:
        """Pack data in SSE format"""
        buffer = ""
        buffer += "id: %s\n" % str(idx)
        buffer += "event: %s\n" % event
        buffer += "data: %s\n" % data
        buffer += "\n"
        return buffer

    @staticmethod
    def __model_file_to_json_dict(model_file: ModelFile) -> dict:
        json_dict = dict()
        json_dict[Serialize.__KEY_FILE_NAME] = model_file.name
        json_dict[Serialize.__KEY_FILE_IS_DIR] = model_file.is_dir
        json_dict[Serialize.__KEY_FILE_STATE] = Serialize.__VALUES_FILE_STATE[model_file.state]
        json_dict[Serialize.__KEY_FILE_REMOTE_SIZE] = model_file.remote_size
        json_dict[Serialize.__KEY_FILE_LOCAL_SIZE] = model_file.local_size
        json_dict[Serialize.__KEY_FILE_DOWNLOADING_SPEED] = model_file.downloading_speed
        json_dict[Serialize.__KEY_FILE_ETA] = model_file.eta
        json_dict[Serialize.__KEY_FILE_FULL_PATH] = model_file.full_path
        json_dict[Serialize.__KEY_FILE_CHILDREN] = list()
        for child in model_file.get_children():
            json_dict[Serialize.__KEY_FILE_CHILDREN].append(Serialize.__model_file_to_json_dict(child))
        return json_dict

    def model(self, model_files: List[ModelFile]) -> str:
        """
        Serialize the model
        :return:
        """
        self.id += 1
        model_json_list = [Serialize.__model_file_to_json_dict(f) for f in model_files]
        model_json = json.dumps(model_json_list)
        return Serialize.__sse_pack(idx=self.id,
                                    event=Serialize.__EVENT_INIT,
                                    data=model_json)

    def update_event(self, event: UpdateEvent):
        self.id += 1
        model_file_json_dict = {
            Serialize.__KEY_UPDATE_OLD_FILE:
                Serialize.__model_file_to_json_dict(event.old_file) if event.old_file else None,
            Serialize.__KEY_UPDATE_NEW_FILE:
                Serialize.__model_file_to_json_dict(event.new_file) if event.new_file else None
        }
        model_file_json = json.dumps(model_file_json_dict)
        return Serialize.__sse_pack(idx=self.id,
                                    event=Serialize.__EVENT_UPDATE[event.change],
                                    data=model_file_json)
