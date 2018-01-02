# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from typing import Optional, List
import time
import copy
from threading import Lock

from ..web_app import IStreamHandler
from ..utils import StreamQueue
from ..serialize import SerializeLogRecord
from common import overrides


class CachedQueueLogHandler(logging.Handler):
    """
    A logging.Handler that caches the past X seconds of
    logs
    """
    def __init__(self, history_size_in_ms: int):
        """
        Constructs a CachedQueueLogHandler
        :param history_size_in_ms: history size, set to 0 to disable caching
        """
        super().__init__()
        self.__history_size_in_ms = history_size_in_ms
        self.__cached_records = []
        self.__cache_lock = Lock()

    def get_cached_records(self) -> List[logging.LogRecord]:
        self.__cache_lock.acquire()
        self.__prune_history()
        cache = copy.copy(self.__cached_records)
        self.__cache_lock.release()
        return cache

    @overrides(logging.Handler)
    def emit(self, record: logging.LogRecord):
        if self.__history_size_in_ms > 0:
            self.__cache_lock.acquire()
            self.__cached_records.append(record)
            self.__prune_history()
            self.__cache_lock.release()

    def __prune_history(self):
        current_time_in_ms = int(time.time()*1000)
        history_start_time_in_ms = current_time_in_ms - self.__history_size_in_ms
        # Find the largest index older than history start time
        prune_index = -1
        for i, record in enumerate(self.__cached_records):
            if 1000.0*record.created < history_start_time_in_ms:
                prune_index = i
            else:
                # assume records are order oldest to newest
                break
        if prune_index >= 0:
            self.__cached_records = self.__cached_records[prune_index+1:]


class QueueLogHandler(logging.Handler, StreamQueue[logging.LogRecord]):
    """
    A log handler that stored records in a thread-safe queue
    """
    def __init__(self):
        logging.Handler.__init__(self)
        StreamQueue.__init__(self)

    @overrides(logging.Handler)
    def emit(self, record):
        self.put(record)


class LogStreamHandler(IStreamHandler):
    """
    Streams logs captured after the stream starts.
    Also cache a small history of logs and sends them when the stream
    starts.
    """
    _CACHE_HISTORY_SIZE_IN_MS = 3000

    # Cache of logs
    _cache = None

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.handler = QueueLogHandler()
        self.serialize = SerializeLogRecord()

    # noinspection PyUnresolvedReferences
    @classmethod
    @overrides(IStreamHandler)
    def register(cls, web_app: "WebApp", **kwargs):
        # Initialize our cache when we register
        LogStreamHandler._cache = CachedQueueLogHandler(
            history_size_in_ms=LogStreamHandler._CACHE_HISTORY_SIZE_IN_MS
        )
        kwargs["logger"].addHandler(LogStreamHandler._cache)

        super().register(web_app=web_app, **kwargs)

    @overrides(IStreamHandler)
    def setup(self):
        # Send out all the cached records first
        for record in LogStreamHandler._cache.get_cached_records():
            self.handler.emit(record)
        # Then subscribe the live stream
        self.logger.addHandler(self.handler)

    @overrides(IStreamHandler)
    def get_value(self) -> Optional[str]:
        record = self.handler.get_next_event()
        if record is not None:
            return self.serialize.record(record)
        else:
            return None

    @overrides(IStreamHandler)
    def cleanup(self):
        self.logger.removeHandler(self.handler)
