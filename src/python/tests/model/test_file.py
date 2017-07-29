# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

from model import ModelFile


class TestModelFile(unittest.TestCase):
    def test_name(self):
        file = ModelFile("test")
        self.assertEqual("test", file.name)

        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            file.name = "new name"

    def test_state(self):
        file = ModelFile("test")

        file.state = ModelFile.State.DELETED_LOCALLY
        self.assertEqual(ModelFile.State.DELETED_LOCALLY, file.state)

        with self.assertRaises(TypeError):
            file.state = "BadState"

    def test_local_size(self):
        file = ModelFile("test")

        file.local_size = 100
        self.assertEqual(100, file.local_size)

        with self.assertRaises(TypeError):
            file.local_size = "BadValue"
        with self.assertRaises(ValueError):
            file.local_size = -100

    def test_remote_size(self):
        file = ModelFile("test")

        file.remote_size = 100
        self.assertEqual(100, file.remote_size)

        with self.assertRaises(TypeError):
            file.remote_size = "BadValue"
        with self.assertRaises(ValueError):
            file.remote_size = -100

    def test_downloading_speed(self):
        file = ModelFile("test")

        file.downloading_speed = 100
        self.assertEqual(100, file.downloading_speed)

        with self.assertRaises(TypeError):
            file.downloading_speed = "BadValue"
        with self.assertRaises(ValueError):
            file.downloading_speed = -100

    def test_update_timestamp(self):
        file = ModelFile("test")

        from datetime import datetime
        now = datetime.now()
        file.update_timestamp = now
        self.assertEqual(now, file.update_timestamp)

        with self.assertRaises(TypeError):
            file.update_timestamp = 100
