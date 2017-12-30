# Copyright 2017, Inderpreet Singh, All rights reserved.

import json
import logging

from .serialize import Serialize


class SerializeLogRecord(Serialize):
    """
    This class defines the serialization interface between python backend
    and the EventSource client frontend for the log stream.
    """
    # Event keys
    __EVENT_RECORD = "log-record"

    # Data keys
    __KEY_TIME = "time"
    __KEY_LEVEL_NAME = "level_name"
    __KEY_LOGGER_NAME = "logger_name"
    __KEY_MESSAGE = "message"

    def record(self, record: logging.LogRecord) -> str:
        json_dict = dict()
        json_dict[SerializeLogRecord.__KEY_TIME] = str(record.created)
        json_dict[SerializeLogRecord.__KEY_LEVEL_NAME] = record.levelname
        json_dict[SerializeLogRecord.__KEY_LOGGER_NAME] = record.name
        json_dict[SerializeLogRecord.__KEY_MESSAGE] = record.msg
        record_json = json.dumps(json_dict)
        return self._sse_pack(event=SerializeLogRecord.__EVENT_RECORD, data=record_json)
