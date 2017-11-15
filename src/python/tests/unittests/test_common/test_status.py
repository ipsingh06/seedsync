# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock

from common import overrides, Status, IStatusListener, StatusComponent, IStatusComponentListener


class DummyStatusComponent(StatusComponent):
    a = StatusComponent._create_property("a")
    b = StatusComponent._create_property("b")

    def __init__(self):
        super().__init__()
        self.a = None
        self.b = None


class DummyStatusComponentListener(IStatusComponentListener):
    @overrides(IStatusComponentListener)
    def notify(self, name):
        pass


class DummyStatusListener(IStatusListener):
    @overrides(IStatusListener)
    def notify(self):
        pass


class TestStatusComponent(unittest.TestCase):
    def test_property_values(self):
        d = DummyStatusComponent()
        d.a = "hello"
        d.b = 33
        self.assertEqual("hello", d.a)
        self.assertEqual(33, d.b)

    def test_listeners(self):
        listener = DummyStatusComponentListener()
        listener.notify = MagicMock()
        d = DummyStatusComponent()
        d.add_listener(listener)
        d.a = "hello world"
        listener.notify.assert_called_once_with("a")
        listener.notify.reset_mock()
        d.b = 44
        listener.notify.assert_called_once_with("b")

        # remove listener
        listener.notify.reset_mock()
        d.remove_listener(listener)
        d.a = "bye world"
        listener.notify.assert_not_called()
        d.b = 22
        listener.notify.assert_not_called()

    def test_copy_values(self):
        d = DummyStatusComponent()
        d.a = "hello world"
        d.b = 55

        e = DummyStatusComponent()
        DummyStatusComponent.copy(d, e)
        self.assertEqual("hello world", e.a)
        self.assertEqual(55, e.b)

        # Modifying original doesn't touch copy
        d.a = "bye world"
        d.b = 66
        self.assertEqual("bye world", d.a)
        self.assertEqual(66, d.b)
        self.assertEqual("hello world", e.a)
        self.assertEqual(55, e.b)

        # Modifying copy doesn't touch original
        e.a = "copied world"
        e.b = 77
        self.assertEqual("bye world", d.a)
        self.assertEqual(66, d.b)
        self.assertEqual("copied world", e.a)
        self.assertEqual(77, e.b)

    def test_copy_doesnt_copy_listeners(self):
        d = DummyStatusComponent()
        d.a = "hello world"
        d.b = 55
        listener = DummyStatusComponentListener()
        listener.notify = MagicMock()
        d.add_listener(listener)

        e = DummyStatusComponent()
        DummyStatusComponent.copy(d, e)

        d.a = "bye world"
        listener.notify.assert_called_once_with("a")
        listener.notify.reset_mock()

        e.a = "copied world"
        listener.notify.assert_not_called()


class TestStatus(unittest.TestCase):
    def test_property_values(self):
        status = Status()
        status.server.up = True
        status.server.error_msg = "Everything's good"
        self.assertEqual(True, status.server.up)
        self.assertEqual("Everything's good", status.server.error_msg)

    def test_listeners(self):
        listener = DummyStatusListener()
        listener.notify = MagicMock()
        status = Status()
        status.add_listener(listener)
        status.server.up = False
        listener.notify.assert_called_once_with()
        listener.notify.reset_mock()
        status.server.error_msg = "Everything's good"
        listener.notify.assert_called_once_with()

    def test_cannot_replace_component(self):
        status = Status()
        new_server = Status.ServerStatus()
        with self.assertRaises(ValueError) as e:
            status.server = new_server
        self.assertEqual("Cannot reassign component", str(e.exception))

    def test_default_values(self):
        status = Status()
        self.assertEqual(True, status.server.up)
        self.assertEqual(None, status.server.error_msg)

    def test_copy_values(self):
        status = Status()
        status.server.up = False
        status.server.error_msg = "Bad error"

        copy = status.copy()
        self.assertEqual(False, copy.server.up)
        self.assertEqual("Bad error", copy.server.error_msg)

        # Modifying original doesn't touch copy
        status.server.up = True
        status.server.error_msg = "No error"
        self.assertEqual(True, status.server.up)
        self.assertEqual("No error", status.server.error_msg)
        self.assertEqual(False, copy.server.up)
        self.assertEqual("Bad error", copy.server.error_msg)

        # Modifying copy doesn't touch original
        copy.server.up = False
        copy.server.error_msg = "Worse error"
        self.assertEqual(True, status.server.up)
        self.assertEqual("No error", status.server.error_msg)
        self.assertEqual(False, copy.server.up)
        self.assertEqual("Worse error", copy.server.error_msg)

    def test_copy_doesnt_copy_listeners(self):
        status = Status()
        listener = DummyStatusListener()
        listener.notify = MagicMock()
        status.add_listener(listener)
        copy = status.copy()

        status.server.error_msg = "a"
        listener.notify.assert_called_once_with()
        listener.notify.reset_mock()

        copy.server.error_msg = "b"
        listener.notify.assert_not_called()
