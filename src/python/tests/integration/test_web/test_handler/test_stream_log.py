# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from unittest.mock import patch
from threading import Timer

from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestLogStreamHandler(BaseTestWebApp):
    @patch("web.handler.stream_log.SerializeLogRecord")
    def test_stream_log_serializes_record(self, mock_serialize_log_record_cls):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        # Schedule status update
        def issue_logs():
            self.context.logger.debug("Debug msg")
            self.context.logger.info("Info msg")
            self.context.logger.warning("Warning msg")
            self.context.logger.error("Error msg")
        Timer(0.3, issue_logs).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_log_record_cls.return_value
        mock_serialize.record.return_value = "\n"

        self.test_app.get("/server/log-stream")
        self.assertEqual(4, len(mock_serialize.record.call_args_list))
        call1, call2, call3, call4 = mock_serialize.record.call_args_list
        record1 = call1[0][0]
        self.assertEqual("Debug msg", record1.msg)
        self.assertEqual(logging.DEBUG, record1.levelno)
        record2 = call2[0][0]
        self.assertEqual("Info msg", record2.msg)
        self.assertEqual(logging.INFO, record2.levelno)
        record3 = call3[0][0]
        self.assertEqual("Warning msg", record3.msg)
        self.assertEqual(logging.WARNING, record3.levelno)
        record4 = call4[0][0]
        self.assertEqual("Error msg", record4.msg)
        self.assertEqual(logging.ERROR, record4.levelno)
