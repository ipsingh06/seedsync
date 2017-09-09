# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
from threading import Timer

from webtest import TestApp

from common import overrides
from web import WebApp, Serialize
from model import ModelFile


class TestWebApp(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        self.context = MagicMock()
        self.controller = MagicMock()

        # Mock the base logger
        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.context.logger = logger

        # Model files
        self.model_files = []

        # Capture the model listener
        def capture_listener(listener):
            self.model_listener = listener
            return self.model_files
        self.model_listener = None
        self.controller.get_model_files_and_add_listener = MagicMock()
        self.controller.get_model_files_and_add_listener.side_effect = capture_listener
        self.controller.remove_model_listener = MagicMock()

        # Note: web test's get() only returns after a request is fully complete
        #       To get around this, we stop the server after a short duration
        self.web_app = WebApp(self.context, self.controller)
        self.test_app = TestApp(self.web_app)

    def test_stream_fetches_model_and_adds_listener(self):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        self.test_app.get("/stream")
        self.controller.get_model_files_and_add_listener.assert_called_once_with(unittest.mock.ANY)

    def test_stream_removes_listener(self):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        self.test_app.get("/stream")
        self.controller.remove_model_listener.assert_called_once_with(self.model_listener)

    @patch("web.web_app.Serialize")
    def test_stream_serializes_initial_model(self, mock_serialize_cls):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_cls.return_value
        mock_serialize.model.return_value = "\n"

        # Initial model
        self.model_files = [ModelFile("a", True), ModelFile("b", False)]

        self.test_app.get("/stream")
        mock_serialize.model.assert_called_once_with([ModelFile("a", True), ModelFile("b", False)])

    @patch("web.web_app.Serialize")
    def test_stream_serializes_updates(self, mock_serialize_cls):
        # Schedule server stop
        Timer(2.0, self.web_app.stop).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_cls.return_value
        mock_serialize.model.return_value = "\n"
        mock_serialize.update_event.return_value = "\n"
        # Use the real UpdateEvent class
        mock_serialize_cls.UpdateEvent = Serialize.UpdateEvent

        # Queue updates
        added_file = ModelFile("a", True)
        removed_file = ModelFile("b", False)
        old_file = ModelFile("c", False)
        old_file.local_size = 100
        new_file = ModelFile("c", False)
        new_file.local_size = 200

        def send_updates():
            self.assertIsNotNone(self.model_listener)
            self.model_listener.file_added(added_file)
            self.model_listener.file_removed(removed_file)
            self.model_listener.file_updated(old_file, new_file)
        Timer(0.5, send_updates).start()

        self.test_app.get("/stream")
        self.assertEqual(3, len(mock_serialize.update_event.call_args_list))
        call1, call2, call3 = mock_serialize.update_event.call_args_list
        self.assertEqual(Serialize.UpdateEvent.Change.ADDED, call1[0][0].change)
        self.assertEqual(None, call1[0][0].old_file)
        self.assertEqual(added_file, call1[0][0].new_file)
        self.assertEqual(Serialize.UpdateEvent.Change.REMOVED, call2[0][0].change)
        self.assertEqual(removed_file, call2[0][0].old_file)
        self.assertEqual(None, call2[0][0].new_file)
        self.assertEqual(Serialize.UpdateEvent.Change.UPDATED, call3[0][0].change)
        self.assertEqual(old_file, call3[0][0].old_file)
        self.assertEqual(new_file, call3[0][0].new_file)
