# Copyright 2017, Inderpreet Singh, All rights reserved.

from abc import ABC


class Serialize(ABC):
    """
    Base class for serialization
    """
    def __init__(self):
        self.__id = -1

    def _sse_pack(self, event: str, data: str) -> str:
        """Pack data in SSE format"""
        self.__id += 1
        buffer = ""
        buffer += "id: %s\n" % str(self.__id)
        buffer += "event: %s\n" % event
        buffer += "data: %s\n" % data
        buffer += "\n"
        return buffer
