# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys

from model import LftpModel, LftpFile, ILftpModelListener, LftpModelError


class DummyLftpModelListener(ILftpModelListener):
    def file_added(self, file: LftpFile):
        pass

    def file_removed(self, file: LftpFile):
        pass

    def file_updated(self, file: LftpFile):
        pass


class TestLftpFile(unittest.TestCase):
    def test_name(self):
        file = LftpFile("test")
        self.assertEqual("test", file.name)

        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            file.name = "new name"

    def test_state(self):
        file = LftpFile("test")

        file.state = LftpFile.State.DELETED_LOCALLY
        self.assertEqual(LftpFile.State.DELETED_LOCALLY, file.state)

        with self.assertRaises(TypeError):
            file.state = "BadState"

    def test_local_size(self):
        file = LftpFile("test")

        file.local_size = 100
        self.assertEqual(100, file.local_size)

        with self.assertRaises(TypeError):
            file.local_size = "BadValue"
        with self.assertRaises(ValueError):
            file.local_size = -100

    def test_remote_size(self):
        file = LftpFile("test")

        file.remote_size = 100
        self.assertEqual(100, file.remote_size)

        with self.assertRaises(TypeError):
            file.remote_size = "BadValue"
        with self.assertRaises(ValueError):
            file.remote_size = -100

    def test_downloading_speed(self):
        file = LftpFile("test")

        file.downloading_speed = 100
        self.assertEqual(100, file.downloading_speed)

        with self.assertRaises(TypeError):
            file.downloading_speed = "BadValue"
        with self.assertRaises(ValueError):
            file.downloading_speed = -100

    def test_update_timestamp(self):
        file = LftpFile("test")

        from datetime import  datetime
        now = datetime.now()
        file.update_timestamp = now
        self.assertEqual(now, file.update_timestamp)

        with self.assertRaises(TypeError):
            file.update_timestamp = 100


class TestLftpModel(unittest.TestCase):
    logger = None

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger(cls.__name__)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        TestLftpModel.logger = logger

    def test_add_file(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        model.add_file(file)
        recv_file = model.get_file("test")
        self.assertEqual("test", recv_file.name)

    def test_get_unknown_file(self):
        model = LftpModel(logger=self.logger)
        with self.assertRaises(LftpModelError):
            model.get_file("test")

    def test_remove_file(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        model.add_file(file)
        model.remove_file(file)
        with self.assertRaises(LftpModelError):
            model.get_file("test")

    def test_remove_unknown_file(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        with self.assertRaises(LftpModelError):
            model.remove_file(file)

    def test_update_file(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        file.local_size = 100
        model.add_file(file)
        recv_file = model.get_file("test")
        self.assertEqual(100, recv_file.local_size)
        recv_file.local_size = 200
        model.update_file(recv_file)
        recv_file = model.get_file("test")
        self.assertEqual(200, recv_file.local_size)

    def test_update_unknown_file(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        with self.assertRaises(LftpModelError):
            model.update_file(file)

    def test_update_local_copy(self):
        model = LftpModel(logger=self.logger)
        file = LftpFile("test")
        file.local_size = 100
        model.add_file(file)
        file.local_size = 200
        recv_file = model.get_file("test")
        # local update should not be reflected in the model
        self.assertEqual(100, recv_file.local_size)

    def test_add_listener(self):
        model = LftpModel(logger=self.logger)
        listener = DummyLftpModelListener()
        model.add_listener(listener)

    def test_listener_file_added(self):
        model = LftpModel(logger=self.logger)
        listener = DummyLftpModelListener()
        model.add_listener(listener)

        listener.file_added = MagicMock()

        file = LftpFile("test")
        model.add_file(file)
        # noinspection PyUnresolvedReferences
        listener.file_added.assert_called_once_with(file)

    def test_listener_file_removed(self):
        model = LftpModel(logger=self.logger)
        listener = DummyLftpModelListener()
        model.add_listener(listener)

        listener.file_removed = MagicMock()

        file = LftpFile("test")
        model.add_file(file)
        model.remove_file(file)
        # noinspection PyUnresolvedReferences
        listener.file_removed.assert_called_once_with(file)

    def test_listener_file_updated(self):
        model = LftpModel(logger=self.logger)
        listener = DummyLftpModelListener()
        model.add_listener(listener)

        listener.file_updated = MagicMock()

        file = LftpFile("test")
        file.local_size = 100
        model.add_file(file)
        file.local_size = 200
        model.update_file(file)
        # noinspection PyUnresolvedReferences
        listener.file_updated.assert_called_once_with(file)

    def test_listener_receives_copies(self):
        model = LftpModel(logger=self.logger)
        listener = DummyLftpModelListener()
        model.add_listener(listener)

        def side_effect(rx_file: LftpFile):
            rx_file.local_size = 200

        listener.file_added = MagicMock()
        listener.file_added.side_effect = side_effect
        listener.file_updated = MagicMock()
        listener.file_updated.side_effect = side_effect

        file = LftpFile("test")
        file.local_size = 100

        # below we check that the side effect is not reflected in the
        # file received from the get_file method

        model.add_file(file)
        # noinspection PyUnresolvedReferences
        self.assertEqual(1, listener.file_added.call_count)
        recv_file = model.get_file("test")
        self.assertEqual(100, recv_file.local_size)

        model.update_file(file)
        # noinspection PyUnresolvedReferences
        self.assertEqual(1, listener.file_updated.call_count)
        recv_file = model.get_file("test")
        self.assertEqual(100, recv_file.local_size)
