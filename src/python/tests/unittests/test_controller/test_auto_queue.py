# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys
import json

from controller import AutoQueue, AutoQueuePersist, Controller
from model import IModelListener, ModelFile


class TestAutoQueuePersist(unittest.TestCase):
    def test_from_str(self):
        content = """
        {
            "patterns": ["one", "two", "th ree", "fo.ur"]
        }
        """
        persist = AutoQueuePersist.from_str(content)
        golden_downloaded = {"one", "two", "th ree", "fo.ur"}
        self.assertEqual(golden_downloaded, persist.patterns)

    def test_to_str(self):
        persist = AutoQueuePersist()
        persist.patterns.add("one")
        persist.patterns.add("two")
        persist.patterns.add("th ree")
        persist.patterns.add("fo.ur")
        dct = json.loads(persist.to_str())
        self.assertTrue("patterns" in dct)
        self.assertEqual({"one", "two", "th ree", "fo.ur"}, set(dct["patterns"]))


class TestAutoQueue(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(TestAutoQueue.__name__)
        handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)

        self.context = MagicMock()

        self.context.logger = self.logger
        self.controller = MagicMock()
        self.controller.get_model_files_and_add_listener = MagicMock()
        self.controller.queue_command = MagicMock()
        self.model_listener = None
        self.initial_model = []

        def capture_listener(listener: IModelListener):
            self.model_listener = listener
            return self.initial_model

        self.controller.get_model_files_and_add_listener.side_effect = capture_listener

    def test_matching_new_files_are_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {
            "File.One",
            "File.Two",
            "File.Three"
        }

        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)

        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_two = ModelFile("File.Two", True)
        file_two.remote_size = 200
        file_three = ModelFile("File.Three", True)
        file_three.remote_size = 300

        self.model_listener.file_added(file_one)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)

        self.model_listener.file_added(file_two)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Two", command.filename)

        self.model_listener.file_added(file_three)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Three", command.filename)

        # All at once
        self.model_listener.file_added(file_one)
        self.model_listener.file_added(file_two)
        self.model_listener.file_added(file_three)
        auto_queue.process()
        calls = self.controller.queue_command.call_args_list[-3:]
        command = calls[0][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)
        command = calls[1][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Two", command.filename)
        command = calls[2][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Three", command.filename)

    def test_matching_initial_files_are_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {
            "File.One",
            "File.Two",
            "File.Three"
        }

        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_two = ModelFile("File.Two", True)
        file_two.remote_size = 200
        file_three = ModelFile("File.Three", True)
        file_three.remote_size = 300
        file_four = ModelFile("File.Four", True)
        file_four.remote_size = 400
        file_five = ModelFile("File.Five", True)
        file_five.remote_size = 500

        self.initial_model = [file_one, file_two, file_three, file_four, file_five]

        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)

        auto_queue.process()

        calls = self.controller.queue_command.call_args_list
        self.assertEqual(3, len(calls))
        command = calls[0][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)
        command = calls[1][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Two", command.filename)
        command = calls[2][0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Three", command.filename)

    def test_matching_is_case_insensitive(self):
        persist = AutoQueuePersist()
        persist.patterns = {
            "FiLe.oNe"
        }
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)

        persist = AutoQueuePersist()
        persist.patterns = {
            "File.One"
        }
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("FiLe.oNe", True)
        file_one.remote_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("FiLe.oNe", command.filename)

    def test_partial_matches(self):
        persist = AutoQueuePersist()
        persist.patterns = {
            "One"
        }
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)

    def test_matching_local_files_are_not_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = None
        file_one.local_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_matching_deleted_files_are_not_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_one.local_size = None
        file_one.state = ModelFile.State.DELETED
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_matching_downloading_files_are_not_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_one.local_size = 0
        file_one.state = ModelFile.State.DOWNLOADING
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()
        file_one_new = ModelFile("File.One", True)
        file_one_new.remote_size = 100
        file_one_new.local_size = 50
        file_one_new.state = ModelFile.State.DOWNLOADING
        self.model_listener.file_updated(file_one, file_one_new)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_matching_queued_files_are_not_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_one.state = ModelFile.State.QUEUED
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_matching_downloaded_files_are_not_queued(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        file_one.state = ModelFile.State.DOWNLOADED
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_auto_queued_file_not_re_queued_after_stopping(self):
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)
        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)

        file_one_updated = ModelFile("File.One", True)
        file_one_updated.remote_size = 100
        file_one_updated.local_size = 50
        self.model_listener.file_updated(file_one, file_one_updated)
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)

    def test_partial_file_is_auto_queued_after_remote_discovery(self):
        # Test that a partial local file is auto-queued when discovered on remote some time later
        persist = AutoQueuePersist()
        persist.patterns = {"File.One"}
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)

        # Local discovery
        file_one = ModelFile("File.One", True)
        file_one.local_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

        # Remote discovery
        file_one_new = ModelFile("File.One", True)
        file_one_new.local_size = 100
        file_one_new.remote_size = 200
        self.model_listener.file_updated(file_one, file_one_new)
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)
