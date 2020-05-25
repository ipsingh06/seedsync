# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from .serialize import Serialize
from common import Status


class SerializeStatusJson:
    # Data keys
    __KEY_SERVER = "server"
    __KEY_SERVER_UP = "up"
    __KEY_SERVER_ERROR_MSG = "error_msg"
    __KEY_CONTROLLER = "controller"
    __KEY_CONTROLLER_LATEST_LOCAL_SCAN_TIME = "latest_local_scan_time"
    __KEY_CONTROLLER_LATEST_REMOTE_SCAN_TIME = "latest_remote_scan_time"

    @staticmethod
    def status(status: Status) -> str:
        json_dict = dict()

        json_dict[SerializeStatusJson.__KEY_SERVER] = dict()
        json_dict[SerializeStatusJson.__KEY_SERVER][SerializeStatusJson.__KEY_SERVER_UP] = \
            status.server.up
        json_dict[SerializeStatusJson.__KEY_SERVER][SerializeStatusJson.__KEY_SERVER_ERROR_MSG] = \
            status.server.error_msg

        json_dict[SerializeStatusJson.__KEY_CONTROLLER] = dict()
        json_dict[SerializeStatusJson.__KEY_CONTROLLER][SerializeStatusJson.__KEY_CONTROLLER_LATEST_LOCAL_SCAN_TIME] = \
            str(status.controller.latest_local_scan_time.timestamp()) \
                if status.controller.latest_local_scan_time else None
        json_dict[SerializeStatusJson.__KEY_CONTROLLER][SerializeStatusJson.__KEY_CONTROLLER_LATEST_REMOTE_SCAN_TIME] = \
            str(status.controller.latest_remote_scan_time.timestamp()) \
                if status.controller.latest_remote_scan_time else None

        status_json = json.dumps(json_dict)
        return status_json


class SerializeStatus(Serialize):
    """
    This class defines the serialization interface between python backend
    and the EventSource client frontend for the status stream.
    """

    # Event keys
    __EVENT_STATUS = "status"

    def status(self, status: Status) -> str:
        status_json = SerializeStatusJson.status(status)
        return self._sse_pack(event=SerializeStatus.__EVENT_STATUS, data=status_json)
