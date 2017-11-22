# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock, patch
from threading import Timer

from tests.integration.test_web.test_web_app import BaseTestWebApp
from web.serialize import SerializeModel
from model import ModelFile


class TestModelStreamHandler(BaseTestWebApp):
    def test_stream_model_fetches_model_and_adds_listener(self):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        self.test_app.get("/server/model-stream")
        self.controller.get_model_files_and_add_listener.assert_called_once_with(unittest.mock.ANY)

    def test_stream_model_removes_listener(self):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        self.test_app.get("/server/model-stream")
        self.controller.remove_model_listener.assert_called_once_with(self.model_listener)

    @patch("web.handler.stream_model.SerializeModel")
    def test_stream_model_serializes_initial_model(self, mock_serialize_model_cls):
        # Schedule server stop
        Timer(0.5, self.web_app.stop).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_model_cls.return_value
        mock_serialize.model.return_value = "\n"

        # Initial model
        self.model_files = [ModelFile("a", True), ModelFile("b", False)]

        self.test_app.get("/server/model-stream")
        mock_serialize.model.assert_called_once_with([ModelFile("a", True), ModelFile("b", False)])

    @patch("web.handler.stream_model.SerializeModel")
    def test_stream_model_serializes_updates(self, mock_serialize_model_cls):
        # Schedule server stop
        Timer(2.0, self.web_app.stop).start()

        # Setup mock serialize instance
        mock_serialize = mock_serialize_model_cls.return_value
        mock_serialize.model.return_value = "\n"
        mock_serialize.update_event.return_value = "\n"
        # Use the real UpdateEvent class
        mock_serialize_model_cls.UpdateEvent = SerializeModel.UpdateEvent

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

        self.test_app.get("/server/model-stream")
        self.assertEqual(3, len(mock_serialize.update_event.call_args_list))
        call1, call2, call3 = mock_serialize.update_event.call_args_list
        self.assertEqual(SerializeModel.UpdateEvent.Change.ADDED, call1[0][0].change)
        self.assertEqual(None, call1[0][0].old_file)
        self.assertEqual(added_file, call1[0][0].new_file)
        self.assertEqual(SerializeModel.UpdateEvent.Change.REMOVED, call2[0][0].change)
        self.assertEqual(removed_file, call2[0][0].old_file)
        self.assertEqual(None, call2[0][0].new_file)
        self.assertEqual(SerializeModel.UpdateEvent.Change.UPDATED, call3[0][0].change)
        self.assertEqual(old_file, call3[0][0].old_file)
        self.assertEqual(new_file, call3[0][0].new_file)
