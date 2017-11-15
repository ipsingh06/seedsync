# Copyright 2017, Inderpreet Singh, All rights reserved.

from unittest.mock import patch
from threading import Timer

from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestStreamStatus(BaseTestWebApp):
    @patch("web.stream_status.SerializeStatus")
    def test_stream_status_serializes_initial_status(self, mock_serialize_status_cls):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_status_cls.return_value
        mock_serialize.status.return_value = "\n"

        self.test_app.get("/server/status-stream")
        self.assertEqual(1, len(mock_serialize.status.call_args_list))
        call1 = mock_serialize.status.call_args_list[0]
        status = call1[0][0]
        self.assertEqual(True, status.server.up)
        self.assertEqual(None, status.server.error_msg)

    @patch("web.stream_status.SerializeStatus")
    def test_stream_status_serializes_new_status(self, mock_serialize_status_cls):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        # Schedule status update
        def update_status():
            self.context.status.server.up = False
            self.context.status.server.error_msg = "Something bad happened"
        Timer(0.3, update_status).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_status_cls.return_value
        mock_serialize.status.return_value = "\n"

        self.test_app.get("/server/status-stream")
        self.assertEqual(3, len(mock_serialize.status.call_args_list))
        call1, call2, call3 = mock_serialize.status.call_args_list
        status1 = call1[0][0]
        self.assertEqual(True, status1.server.up)
        self.assertEqual(None, status1.server.error_msg)
        status2 = call2[0][0]
        self.assertEqual(False, status2.server.up)
        self.assertEqual(None, status2.server.error_msg)
        status3 = call3[0][0]
        self.assertEqual(False, status3.server.up)
        self.assertEqual("Something bad happened", status3.server.error_msg)
