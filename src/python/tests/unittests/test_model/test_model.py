# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
import unittest
from unittest.mock import MagicMock

from common import overrides
from model import Model, ModelFile, IModelListener, ModelError


class DummyModelListener(IModelListener):
    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        pass

    @overrides(IModelListener)
    def file_removed(self, file: ModelFile):
        pass

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        pass


class TestLftpModel(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger(TestLftpModel.__name__)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.model = Model()
        self.model.set_base_logger(logger)

    def test_add_file(self):
        file = ModelFile("test", False)
        self.model.add_file(file)
        recv_file = self.model.get_file("test")
        self.assertEqual("test", recv_file.name)

    def test_get_unknown_file(self):
        with self.assertRaises(ModelError):
            self.model.get_file("test")

    def test_remove_file(self):
        file = ModelFile("test", False)
        self.model.add_file(file)
        self.model.remove_file("test")
        with self.assertRaises(ModelError):
            self.model.get_file("test")

    def test_remove_unknown_file(self):
        with self.assertRaises(ModelError):
            self.model.remove_file("test")

    def test_update_file(self):
        file = ModelFile("test", False)
        file.local_size = 100
        self.model.add_file(file)
        recv_file = self.model.get_file("test")
        self.assertEqual(100, recv_file.local_size)
        recv_file.local_size = 200
        self.model.update_file(recv_file)
        recv_file = self.model.get_file("test")
        self.assertEqual(200, recv_file.local_size)

    def test_update_unknown_file(self):
        file = ModelFile("test", False)
        with self.assertRaises(ModelError):
            self.model.update_file(file)

    def test_get_file_names(self):
        self.assertEqual(set(), self.model.get_file_names())
        self.model.add_file(ModelFile("a", False))
        self.assertEqual({"a"}, self.model.get_file_names())
        self.model.add_file(ModelFile("b", False))
        self.assertEqual({"a", "b"}, self.model.get_file_names())
        self.model.add_file(ModelFile("c", False))
        self.assertEqual({"a", "b", "c"}, self.model.get_file_names())
        self.model.remove_file("b")
        self.assertEqual({"a", "c"}, self.model.get_file_names())
        self.model.add_file(ModelFile("d", False))
        self.assertEqual({"a", "c", "d"}, self.model.get_file_names())

    def test_add_listener(self):
        listener = DummyModelListener()
        self.model.add_listener(listener)

    def test_listener_file_added(self):
        listener = DummyModelListener()
        self.model.add_listener(listener)

        listener.file_added = MagicMock()

        file = ModelFile("test", False)
        self.model.add_file(file)
        # noinspection PyUnresolvedReferences
        listener.file_added.assert_called_once_with(file)

    def test_listener_file_removed(self):
        listener = DummyModelListener()
        self.model.add_listener(listener)

        listener.file_removed = MagicMock()

        file = ModelFile("test", False)
        self.model.add_file(file)
        self.model.remove_file("test")
        # noinspection PyUnresolvedReferences
        listener.file_removed.assert_called_once_with(file)

    def test_listener_file_updated(self):
        listener = DummyModelListener()
        self.model.add_listener(listener)

        listener.file_updated = MagicMock()

        old_file = ModelFile("test", False)
        old_file.local_size = 100
        self.model.add_file(old_file)
        new_file = ModelFile("test", False)
        new_file.local_size = 200
        self.model.update_file(new_file)
        # noinspection PyUnresolvedReferences
        listener.file_updated.assert_called_once_with(old_file, new_file)
