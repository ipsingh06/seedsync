# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from typing import Optional

from ..web_app import IStreamHandler
from ..utils import StreamQueue
from ..serialize import SerializeLogRecord
from common import overrides


class QueueLogHandler(logging.Handler, StreamQueue[logging.LogRecord]):
    """
    A log handler that stored records in a thread-safe queue
    """
    def __init__(self):
        logging.Handler.__init__(self)
        StreamQueue.__init__(self)

    def emit(self, record):
        self.put(record)


class LogStreamHandler(IStreamHandler):
    _EVENT_BLOCK_INTERVAL_IN_MS = 500

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.handler = QueueLogHandler()
        self.serialize = SerializeLogRecord()

    @staticmethod
    @overrides(IStreamHandler)
    def get_path() -> str:
        return "/server/log-stream"

    @overrides(IStreamHandler)
    def setup(self):
        self.logger.addHandler(self.handler)

    @overrides(IStreamHandler)
    def get_value(self) -> Optional[str]:
        record = self.handler.get_next_event(timeout_in_ms=LogStreamHandler._EVENT_BLOCK_INTERVAL_IN_MS)
        if record:
            return self.serialize.record(record)
        else:
            return None

    @overrides(IStreamHandler)
    def cleanup(self):
        self.logger.removeHandler(self.handler)
