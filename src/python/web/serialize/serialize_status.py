# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from .serialize import Serialize
from common import Status


class SerializeStatus(Serialize):
    """
    This class defines the serialization interface between python backend
    and the EventSource client frontend for the status stream.
    """
    # Event keys
    __EVENT_STATUS = "status"

    # Data keys
    __KEY_SERVER = "server"
    __KEY_SERVER_UP = "up"
    __KEY_SERVER_ERROR_MSG = "error_msg"

    def status(self, status: Status) -> str:
        json_dict = dict()
        json_dict[SerializeStatus.__KEY_SERVER] = dict()
        json_dict[SerializeStatus.__KEY_SERVER][SerializeStatus.__KEY_SERVER_UP] = status.server.up
        json_dict[SerializeStatus.__KEY_SERVER][SerializeStatus.__KEY_SERVER_ERROR_MSG] = status.server.error_msg
        status_json = json.dumps(json_dict)
        return self._sse_pack(event=SerializeStatus.__EVENT_STATUS, data=status_json)
