# Copyright 2017, Inderpreet Singh, All rights reserved.

from abc import ABC


class Serialize(ABC):
    """
    Base class for serialization
    """
    def __init__(self):
        self.id = -1

    def _sse_pack(self, event: str, data: str) -> str:
        """Pack data in SSE format"""
        self.id += 1
        buffer = ""
        buffer += "id: %s\n" % str(self.id)
        buffer += "event: %s\n" % event
        buffer += "data: %s\n" % data
        buffer += "\n"
        return buffer
