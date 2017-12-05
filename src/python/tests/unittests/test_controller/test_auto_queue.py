# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys
import json

from common import overrides, PersistError
from controller import AutoQueue, AutoQueuePersist, IAutoQueuePersistListener, AutoQueuePattern
from controller import Controller
from model import IModelListener, ModelFile


class TestAutoQueuePattern(unittest.TestCase):
    def test_pattern(self):
        aqp = AutoQueuePattern(pattern="file.one")
        self.assertEqual(aqp.pattern, "file.one")
        aqp = AutoQueuePattern(pattern="file.two")
        self.assertEqual(aqp.pattern, "file.two")

    def test_equality(self):
        aqp_1 = AutoQueuePattern(pattern="file.one")
        aqp_2 = AutoQueuePattern(pattern="file.two")
        aqp_1b = AutoQueuePattern(pattern="file.one")
        self.assertEqual(aqp_1, aqp_1b)
        self.assertNotEqual(aqp_1, aqp_2)

    def test_to_str(self):
        self.assertEqual(
            "{\"pattern\": \"file.one\"}",
            AutoQueuePattern(pattern="file.one").to_str()
        )
        self.assertEqual(
            "{\"pattern\": \"file'one\"}",
            AutoQueuePattern(pattern="file'one").to_str()
        )
        self.assertEqual(
            "{\"pattern\": \"file\\\"one\"}",
            AutoQueuePattern(pattern="file\"one").to_str()
        )
        self.assertEqual(
            "{\"pattern\": \"fil(eo)ne\"}",
            AutoQueuePattern(pattern="fil(eo)ne").to_str()
        )

    def test_from_str(self):
        self.assertEqual(
            AutoQueuePattern(pattern="file.one"),
            AutoQueuePattern.from_str("{\"pattern\": \"file.one\"}"),
        )
        self.assertEqual(
            AutoQueuePattern(pattern="file'one"),
            AutoQueuePattern.from_str("{\"pattern\": \"file'one\"}"),
        )
        self.assertEqual(
            AutoQueuePattern(pattern="file\"one"),
            AutoQueuePattern.from_str("{\"pattern\": \"file\\\"one\"}"),
        )
        self.assertEqual(
            AutoQueuePattern(pattern="fil(eo)ne"),
            AutoQueuePattern.from_str("{\"pattern\": \"fil(eo)ne\"}"),
        )

    def test_to_and_from_str(self):
        self.assertEqual(
            AutoQueuePattern(pattern="file.one"),
            AutoQueuePattern.from_str(AutoQueuePattern(pattern="file.one").to_str())
        )
        self.assertEqual(
            AutoQueuePattern(pattern="file'one"),
            AutoQueuePattern.from_str(AutoQueuePattern(pattern="file'one").to_str())
        )
        self.assertEqual(
            AutoQueuePattern(pattern="file\"one"),
            AutoQueuePattern.from_str(AutoQueuePattern(pattern="file\"one").to_str())
        )
        self.assertEqual(
            AutoQueuePattern(pattern="fil(eo)ne"),
            AutoQueuePattern.from_str(AutoQueuePattern(pattern="fil(eo)ne").to_str())
        )


class TestAutoQueuePersistListener(IAutoQueuePersistListener):
    @overrides(IAutoQueuePersistListener)
    def pattern_added(self, pattern: AutoQueuePattern):
        pass

    @overrides(IAutoQueuePersistListener)
    def pattern_removed(self, pattern: AutoQueuePattern):
        pass


class TestAutoQueuePersist(unittest.TestCase):
    def test_add_pattern(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        self.assertEqual({
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="two")
        }, persist.patterns)
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="three"))
        self.assertEqual({
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="two"),
            AutoQueuePattern(pattern="three")
        }, persist.patterns)

    def test_add_blank_pattern_fails(self):
        persist = AutoQueuePersist()
        with self.assertRaises(ValueError):
            persist.add_pattern(AutoQueuePattern(pattern=""))
        with self.assertRaises(ValueError):
            persist.add_pattern(AutoQueuePattern(pattern=" "))
        with self.assertRaises(ValueError):
            persist.add_pattern(AutoQueuePattern(pattern="   "))

    def test_remove_pattern(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        persist.remove_pattern(AutoQueuePattern(pattern="one"))
        self.assertEqual({AutoQueuePattern(pattern="two")}, persist.patterns)
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="three"))
        persist.remove_pattern(AutoQueuePattern(pattern="two"))
        self.assertEqual({
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="three")
        }, persist.patterns)

    def test_listener_pattern_added(self):
        listener = TestAutoQueuePersistListener()
        listener.pattern_added = MagicMock()
        persist = AutoQueuePersist()
        persist.add_listener(listener)
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        listener.pattern_added.assert_called_once_with(AutoQueuePattern(pattern="one"))
        listener.pattern_added.reset_mock()
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        listener.pattern_added.assert_called_once_with(AutoQueuePattern(pattern="two"))
        listener.pattern_added.reset_mock()

    def test_listener_pattern_added_duplicate(self):
        listener = TestAutoQueuePersistListener()
        listener.pattern_added = MagicMock()
        persist = AutoQueuePersist()
        persist.add_listener(listener)
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        listener.pattern_added.assert_called_once_with(AutoQueuePattern(pattern="one"))
        listener.pattern_added.reset_mock()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        listener.pattern_added.assert_not_called()

    def test_listener_pattern_removed(self):
        listener = TestAutoQueuePersistListener()
        listener.pattern_removed = MagicMock()
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        persist.add_pattern(AutoQueuePattern(pattern="three"))
        persist.add_listener(listener)
        persist.remove_pattern(AutoQueuePattern(pattern="one"))
        listener.pattern_removed.assert_called_once_with(AutoQueuePattern(pattern="one"))
        listener.pattern_removed.reset_mock()
        persist.remove_pattern(AutoQueuePattern(pattern="two"))
        listener.pattern_removed.assert_called_once_with(AutoQueuePattern(pattern="two"))
        listener.pattern_removed.reset_mock()

    def test_listener_pattern_removed_non_existing(self):
        listener = TestAutoQueuePersistListener()
        listener.pattern_removed = MagicMock()
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        persist.add_pattern(AutoQueuePattern(pattern="three"))
        persist.add_listener(listener)
        persist.remove_pattern(AutoQueuePattern(pattern="four"))
        listener.pattern_removed.assert_not_called()

    # {
    #     "patterns": [
    #         "{\"pattern\": \"one\"}",
    #         "{\"pattern\": \"two\"}",
    #         "{\"pattern\": \"th ree\"}",
    #         "{\"pattern\": \"fo.ur\"}",
    #         "{\"pattern\": \"fi\\\"ve\"}",
    #         "{\"pattern\": \"si'x\"}"
    #     ]
    # }

    def test_from_str(self):
        content = """
        {{
            "patterns": [
                "{}",
                "{}",
                "{}",
                "{}",
                "{}",
                "{}"
            ]
        }}
        """.format(
            AutoQueuePattern(pattern="one").to_str().replace("\\", "\\\\").replace("\"", "\\\""),
            AutoQueuePattern(pattern="two").to_str().replace("\\", "\\\\").replace("\"", "\\\""),
            AutoQueuePattern(pattern="th ree").to_str().replace("\\", "\\\\").replace("\"", "\\\""),
            AutoQueuePattern(pattern="fo.ur").to_str().replace("\\", "\\\\").replace("\"", "\\\""),
            AutoQueuePattern(pattern="fi\"ve").to_str().replace("\\", "\\\\").replace("\"", "\\\""),
            AutoQueuePattern(pattern="si'x").to_str().replace("\\", "\\\\").replace("\"", "\\\"")
        )
        print(content)
        print(AutoQueuePattern(pattern="fi\"ve").to_str())
        persist = AutoQueuePersist.from_str(content)
        golden_patterns = {
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="two"),
            AutoQueuePattern(pattern="th ree"),
            AutoQueuePattern(pattern="fo.ur"),
            AutoQueuePattern(pattern="fi\"ve"),
            AutoQueuePattern(pattern="si'x")
        }
        self.assertEqual(golden_patterns, persist.patterns)

    def test_to_str(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        persist.add_pattern(AutoQueuePattern(pattern="th ree"))
        persist.add_pattern(AutoQueuePattern(pattern="fo.ur"))
        persist.add_pattern(AutoQueuePattern(pattern="fi\"ve"))
        persist.add_pattern(AutoQueuePattern(pattern="si'x"))
        print(persist.to_str())
        dct = json.loads(persist.to_str())
        self.assertTrue("patterns" in dct)
        self.assertEqual(
            [
                AutoQueuePattern(pattern="one").to_str(),
                AutoQueuePattern(pattern="two").to_str(),
                AutoQueuePattern(pattern="th ree").to_str(),
                AutoQueuePattern(pattern="fo.ur").to_str(),
                AutoQueuePattern(pattern="fi\"ve").to_str(),
                AutoQueuePattern(pattern="si'x").to_str()
            ],
            dct["patterns"]
        )

    def test_to_and_from_str(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="one"))
        persist.add_pattern(AutoQueuePattern(pattern="two"))
        persist.add_pattern(AutoQueuePattern(pattern="th ree"))
        persist.add_pattern(AutoQueuePattern(pattern="fo.ur"))
        persist.add_pattern(AutoQueuePattern(pattern="fi\"ve"))
        persist.add_pattern(AutoQueuePattern(pattern="si'x"))

        persist_actual = AutoQueuePersist.from_str(persist.to_str())
        self.assertEqual(
            persist.patterns,
            persist_actual.patterns
        )

    def test_persist_read_error(self):
        # bad pattern
        content = """
        {
            "patterns": [
                "bad string"
            ]
        }
        """
        with self.assertRaises(PersistError):
            AutoQueuePersist.from_str(content)

        # empty json
        content = ""
        with self.assertRaises(PersistError):
            AutoQueuePersist.from_str(content)

        # missing keys
        content = "{}"
        with self.assertRaises(PersistError):
            AutoQueuePersist.from_str(content)

        # malformed
        content = "{"
        with self.assertRaises(PersistError):
            AutoQueuePersist.from_str(content)


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

        def get_model():
            return self.initial_model

        def get_model_and_capture_listener(listener: IModelListener):
            self.model_listener = listener
            return get_model()

        self.controller.get_model_files.side_effect = get_model
        self.controller.get_model_files_and_add_listener.side_effect = get_model_and_capture_listener

    def test_matching_new_files_are_queued(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
        persist.add_pattern(AutoQueuePattern(pattern="File.Two"))
        persist.add_pattern(AutoQueuePattern(pattern="File.Three"))

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
        commands = [calls[i][0][0] for i in range(3)]
        self.assertEqual(set([Controller.Command.Action.QUEUE]*3), {c.action for c in commands})
        self.assertEqual({"File.One", "File.Two", "File.Three"}, {c.filename for c in commands})

    def test_matching_initial_files_are_queued(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
        persist.add_pattern(AutoQueuePattern(pattern="File.Two"))
        persist.add_pattern(AutoQueuePattern(pattern="File.Three"))

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
        commands = [calls[i][0][0] for i in range(3)]
        self.assertEqual(set([Controller.Command.Action.QUEUE]*3), {c.action for c in commands})
        self.assertEqual({"File.One", "File.Two", "File.Three"}, {c.filename for c in commands})

    def test_matching_is_case_insensitive(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="FiLe.oNe"))

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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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
        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
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

    def test_new_matching_pattern_queues_existing_files(self):
        persist = AutoQueuePersist()

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
        self.controller.queue_command.assert_not_called()

        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)
        self.controller.queue_command.reset_mock()

        persist.add_pattern(AutoQueuePattern(pattern="File.Two"))
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Two", command.filename)
        self.controller.queue_command.reset_mock()

        persist.add_pattern(AutoQueuePattern(pattern="File.Three"))
        auto_queue.process()
        self.controller.queue_command.assert_called_once_with(unittest.mock.ANY)
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.Three", command.filename)
        self.controller.queue_command.reset_mock()

        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_new_matching_pattern_doesnt_queue_local_file(self):
        persist = AutoQueuePersist()

        file_one = ModelFile("File.One", True)
        file_one.local_size = 100

        self.initial_model = [file_one]

        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)

        auto_queue.process()
        self.controller.queue_command.assert_not_called()

        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_removed_pattern_doesnt_queue_new_file(self):
        persist = AutoQueuePersist()
        persist.add_pattern(AutoQueuePattern(pattern="One"))
        persist.add_pattern(AutoQueuePattern(pattern="Two"))
        # noinspection PyTypeChecker
        auto_queue = AutoQueue(self.context, persist, self.controller)

        file_one = ModelFile("File.One", True)
        file_one.remote_size = 100
        self.model_listener.file_added(file_one)
        auto_queue.process()
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("File.One", command.filename)
        self.controller.queue_command.reset_mock()

        persist.remove_pattern(AutoQueuePattern(pattern="Two"))

        file_two = ModelFile("File.Two", True)
        file_two.remote_size = 100
        self.model_listener.file_added(file_two)
        auto_queue.process()
        self.controller.queue_command.assert_not_called()

    def test_adding_then_removing_pattern_doesnt_queue_existing_file(self):
        persist = AutoQueuePersist()

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
        self.controller.queue_command.assert_not_called()

        persist.add_pattern(AutoQueuePattern(pattern="File.One"))
        persist.remove_pattern(AutoQueuePattern(pattern="File.One"))
        auto_queue.process()
        self.controller.queue_command.assert_not_called()
