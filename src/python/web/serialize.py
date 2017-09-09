# Copyright 2017, Inderpreet Singh, All rights reserved.

from enum import Enum
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

    @staticmethod
    def __sse_pack(id: int, event: str, data: str) -> str:
        """Pack data in SSE format"""
        buffer = ""
        buffer += "id: %s\n" % str(id)
        buffer += "event: %s\n" % event
        buffer += "data: %s\n" % data
        buffer += "\n"
        return buffer

    def model(self, model_files: List[ModelFile]) -> str:
        """
        Serialize the model
        :return:
        """
        self.id += 1
        return Serialize.__sse_pack(id=self.id,
                                    event="init",
                                    data="full model")

    def update_event(self, event: UpdateEvent):
        self.id += 1
        return Serialize.__sse_pack(id=self.id,
                                    event="event",
                                    data=event.new_file.name)
