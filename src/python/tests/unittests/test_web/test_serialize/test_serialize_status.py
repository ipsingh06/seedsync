# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json
from datetime import datetime
from pytz import timezone

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

        timestamp = datetime(2018, 11, 9, 21, 40, 18, tzinfo=timezone('UTC'))
        status.controller.latest_local_scan_time = timestamp
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(str(1541799618.0), data["controller"]["latest_local_scan_time"])

    def test_controller_status_latest_remote_scan_time(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertIsNone(data["controller"]["latest_remote_scan_time"])

        timestamp = datetime(2018, 11, 9, 21, 40, 18, tzinfo=timezone('UTC'))
        status.controller.latest_remote_scan_time = timestamp
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(str(1541799618.0), data["controller"]["latest_remote_scan_time"])

    def test_controller_status_latest_remote_scan_failed(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertIsNone(data["controller"]["latest_remote_scan_failed"])

        status.controller.latest_remote_scan_failed = True
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual(True, data["controller"]["latest_remote_scan_failed"])

    def test_controller_status_latest_remote_scan_error(self):
        serialize = SerializeStatus()
        status = Status()
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertIsNone(data["controller"]["latest_remote_scan_error"])

        status.controller.latest_remote_scan_error = "remote server went boom"
        out = parse_stream(serialize.status(status))
        data = json.loads(out["data"])
        self.assertEqual("remote server went boom", data["controller"]["latest_remote_scan_error"])
