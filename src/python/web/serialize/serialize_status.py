# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from .serialize import Serialize
from common import Status
from datetime import datetime
import time


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
    __KEY_CONTROLLER = "controller"
    __KEY_CONTROLLER_LATEST_LOCAL_SCAN_TIME = "latest_local_scan_time"
    __KEY_CONTROLLER_LATEST_REMOTE_SCAN_TIME = "latest_remote_scan_time"

    def status(self, status: Status) -> str:
        json_dict = dict()

        json_dict[SerializeStatus.__KEY_SERVER] = dict()
        json_dict[SerializeStatus.__KEY_SERVER][SerializeStatus.__KEY_SERVER_UP] = \
            status.server.up
        json_dict[SerializeStatus.__KEY_SERVER][SerializeStatus.__KEY_SERVER_ERROR_MSG] = \
            status.server.error_msg

        json_dict[SerializeStatus.__KEY_CONTROLLER] = dict()
        json_dict[SerializeStatus.__KEY_CONTROLLER][SerializeStatus.__KEY_CONTROLLER_LATEST_LOCAL_SCAN_TIME] = \
            str(SerializeStatus.__datetime_to_time(status.controller.latest_local_scan_time)) \
                if status.controller.latest_local_scan_time else None
        json_dict[SerializeStatus.__KEY_CONTROLLER][SerializeStatus.__KEY_CONTROLLER_LATEST_REMOTE_SCAN_TIME] = \
            str(SerializeStatus.__datetime_to_time(status.controller.latest_remote_scan_time)) \
                if status.controller.latest_remote_scan_time else None

        status_json = json.dumps(json_dict)
        return self._sse_pack(event=SerializeStatus.__EVENT_STATUS, data=status_json)

    @staticmethod
    def __datetime_to_time(timestamp: datetime) -> float:
        return time.mktime(timestamp.timetuple()) + timestamp.microsecond / 1E6
