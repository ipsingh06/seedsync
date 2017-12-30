# Copyright 2017, Inderpreet Singh, All rights reserved.

from abc import ABC


class Serialize(ABC):
    """
    Base class for serialization
    """
    # noinspection PyMethodMayBeStatic
    def _sse_pack(self, event: str, data: str) -> str:
        """Pack data in SSE format"""
        buffer = ""
        buffer += "event: %s\n" % event
        buffer += "data: %s\n" % data
        buffer += "\n"
        return buffer
