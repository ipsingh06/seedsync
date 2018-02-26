# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json
from datetime import datetime
import time

from .test_serialize import parse_stream
from common import Status
from web.serialize import SerializeStatus


class TestSerializeStatus(unittest.TestCase):
    def test_event_names(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        self.assertEqual("status", out["event"])

        status.server.up = False
        status.server.error_msg = "Bad stuff happened"
        out = parse_stream(serialize.status(status))
        self.assertEqual("status", out["event"])

    def test_server_status_up(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(True, data["server"]["up"])

        status.server.up = False
        status.server.error_msg = "Bad stuff happened"
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(False, data["server"]["up"])

    def test_server_status_error_msg(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(None, data["server"]["error_msg"])

        status.server.up = False
        status.server.error_msg = "Bad stuff happened"
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual("Bad stuff happened", data["server"]["error_msg"])

    def test_controller_status_latest_local_scan_time(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertIsNone(data["controller"]["latest_local_scan_time"])

        timestamp = datetime.now()
        time_float = time.mktime(timestamp.timetuple()) + timestamp.microsecond / 1E6
        status.controller.latest_local_scan_time = timestamp
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(str(time_float), data["controller"]["latest_local_scan_time"])

    def test_controller_status_latest_remote_scan_time(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertIsNone(data["controller"]["latest_remote_scan_time"])

        timestamp = datetime.now()
        time_float = time.mktime(timestamp.timetuple()) + timestamp.microsecond / 1E6
        status.controller.latest_remote_scan_time = timestamp
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(str(time_float), data["controller"]["latest_remote_scan_time"])
