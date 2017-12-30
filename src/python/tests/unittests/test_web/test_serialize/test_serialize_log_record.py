# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json
import logging

from .test_serialize import parse_stream
from web.serialize import SerializeLogRecord


class TestSerializeLogRecord(unittest.TestCase):
    def test_event_names(self):
        serialize = SerializeLogRecord()
        logger = logging.getLogger()
        record = logger.makeRecord(
            name=None,
            level=None,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        out = parse_stream(serialize.record(record))
        self.assertEqual("log-record", out["event"])

    def test_record_time(self):
        serialize = SerializeLogRecord()
        logger = logging.getLogger()
        record = logger.makeRecord(
            name=None,
            level=None,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual(str(record.created), data["time"])

    def test_record_level_name(self):
        serialize = SerializeLogRecord()
        logger = logging.getLogger()

        record = logger.makeRecord(
            name=None,
            level=logging.DEBUG,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        print(record.name)
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("DEBUG", data["level_name"])

        record = logger.makeRecord(
            name=None,
            level=logging.INFO,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        print(record.name)
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("INFO", data["level_name"])

        record = logger.makeRecord(
            name=None,
            level=logging.WARNING,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        print(record.name)
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("WARNING", data["level_name"])

        record = logger.makeRecord(
            name=None,
            level=logging.ERROR,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        print(record.name)
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("ERROR", data["level_name"])

        record = logger.makeRecord(
            name=None,
            level=logging.CRITICAL,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        print(record.name)
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("CRITICAL", data["level_name"])

    def test_record_logger_name(self):
        serialize = SerializeLogRecord()
        logger = logging.getLogger()
        record = logger.makeRecord(
            name="myloggername",
            level=None,
            fn=None,
            lno=None,
            msg=None,
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("myloggername", data["logger_name"])

    def test_record_message(self):
        serialize = SerializeLogRecord()
        logger = logging.getLogger()
        record = logger.makeRecord(
            name=None,
            level=None,
            fn=None,
            lno=None,
            msg="my logger msg",
            args=None,
            exc_info=None,
            func=None,
            sinfo=None
        )
        out = parse_stream(serialize.record(record))
        data = json.loads(out["data"])
        self.assertEqual("my logger msg", data["message"])
