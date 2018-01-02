# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import patch
from logging import LogRecord

from web.handler.stream_log import CachedQueueLogHandler


def create_log_record(created: float, msg: str) -> LogRecord:
    record = LogRecord(
        name=None,
        level=None,
        pathname=None,
        lineno=None,
        msg=msg,
        args=None,
        exc_info=None
    )
    record.created = created
    return record


class TestCachedQueueLogHandler(unittest.TestCase):
    @patch("web.handler.stream_log.time")
    def test_caches_new_records(self, mock_time_module):
        time_func = mock_time_module.time

        cache = CachedQueueLogHandler(history_size_in_ms=3000)

        # Set current time at 10000 ms
        time_func.return_value = 10.0

        # Create some records between 7000 ms - 10000 ms
        record1 = create_log_record(7.5, "record1")
        record2 = create_log_record(8.5, "record2")
        record3 = create_log_record(9.5, "record3")

        # Pass them to cache
        cache.emit(record1)
        cache.emit(record2)
        cache.emit(record3)

        # Get cached record, all of them should be there
        actual = cache.get_cached_records()
        self.assertEqual(3, len(actual))
        self.assertEqual("record1", actual[0].msg)
        self.assertEqual(7.5, actual[0].created)
        self.assertEqual("record2", actual[1].msg)
        self.assertEqual(8.5, actual[1].created)
        self.assertEqual("record3", actual[2].msg)
        self.assertEqual(9.5, actual[2].created)

    @patch("web.handler.stream_log.time")
    def test_prunes_old_records(self, mock_time_module):
        time_func = mock_time_module.time

        cache = CachedQueueLogHandler(history_size_in_ms=3000)

        # Set current time at 10000 ms
        time_func.return_value = 10.0

        # Create some records between 0 ms - 10000 ms
        record1 = create_log_record(0.5, "record1")
        record2 = create_log_record(5.5, "record2")
        record3 = create_log_record(7.5, "record3")
        record4 = create_log_record(9.5, "record4")

        # Pass them to cache
        cache.emit(record1)
        cache.emit(record2)
        cache.emit(record3)
        cache.emit(record4)

        # Get cached record, only newer than 7000ms should be there
        actual = cache.get_cached_records()
        self.assertEqual(2, len(actual))
        self.assertEqual("record3", actual[0].msg)
        self.assertEqual(7.5, actual[0].created)
        self.assertEqual("record4", actual[1].msg)
        self.assertEqual(9.5, actual[1].created)

    @patch("web.handler.stream_log.time")
    def test_prunes_old_records_at_get_time(self, mock_time_module):
        time_func = mock_time_module.time

        cache = CachedQueueLogHandler(history_size_in_ms=3000)

        # Set current time at 10000 ms
        time_func.return_value = 10.0

        # Create some records between 7000 ms - 10000 ms
        record1 = create_log_record(7.5, "record1")
        record2 = create_log_record(8.5, "record2")
        record3 = create_log_record(9.5, "record3")
        record4 = create_log_record(10.0, "record4")

        # Pass them to cache
        cache.emit(record1)
        cache.emit(record2)
        cache.emit(record3)
        cache.emit(record4)

        # Now set the current time to 12000 ms
        time_func.return_value = 12.0

        # Get cached record, only newer than 9000ms should be there
        actual = cache.get_cached_records()
        self.assertEqual(2, len(actual))
        self.assertEqual("record3", actual[0].msg)
        self.assertEqual(9.5, actual[0].created)
        self.assertEqual("record4", actual[1].msg)
        self.assertEqual(10.0, actual[1].created)

    @patch("web.handler.stream_log.time")
    def test_cache_can_be_disabled(self, mock_time_module):
        time_func = mock_time_module.time

        cache = CachedQueueLogHandler(history_size_in_ms=0)

        # Set current time at 10000 ms
        time_func.return_value = 10.0

        # Create some records in past and future
        record1 = create_log_record(7.5, "record1")
        record2 = create_log_record(10.0, "record2")
        record3 = create_log_record(11.5, "record3")

        # Pass them to cache
        cache.emit(record1)
        cache.emit(record2)
        cache.emit(record3)

        # Get cached record, should return nothing
        actual = cache.get_cached_records()
        self.assertEqual(0, len(actual))
