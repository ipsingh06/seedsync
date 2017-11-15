# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys

from webtest import TestApp

from common import overrides, Status
from web import WebApp
from controller import Controller


class BaseTestWebApp(unittest.TestCase):
    """
    Base class for testing web app
    Sets up the web app with mocks
    """
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

        # Real status
        self.context.status = Status()

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
        # noinspection PyTypeChecker
        self.web_app = WebApp(self.context, self.controller)
        self.test_app = TestApp(self.web_app)


class TestWebApp(BaseTestWebApp):
    def test_restart(self):
        self.assertFalse(self.web_app.is_restart_requested())
        print(self.test_app.get("/server/command/restart"))
        self.assertTrue(self.web_app.is_restart_requested())
        print(self.test_app.get("/server/command/restart"))
        self.assertTrue(self.web_app.is_restart_requested())

    def test_queue(self):
        def side_effect(cmd: Controller.Command):
            cmd.callbacks[0].on_success()
        self.controller.queue_command = MagicMock()
        self.controller.queue_command.side_effect = side_effect
        print(self.test_app.get("/server/command/queue/test1"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("test1", command.filename)
        print(self.test_app.get("/server/command/queue/Really.Cool.Show"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("Really.Cool.Show", command.filename)
        print(self.test_app.get("/server/command/queue/Really.Cool.Show.mp4"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("Really.Cool.Show.mp4", command.filename)
        print(self.test_app.get("/server/command/queue/Really.Cool.Show%20%20With%20%20Spaces"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("Really.Cool.Show  With  Spaces", command.filename)

    def test_stop(self):
        def side_effect(cmd: Controller.Command):
            cmd.callbacks[0].on_success()
        self.controller.queue_command = MagicMock()
        self.controller.queue_command.side_effect = side_effect
        print(self.test_app.get("/server/command/stop/test1"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("test1", command.filename)
        print(self.test_app.get("/server/command/stop/Really.Cool.Show"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("Really.Cool.Show", command.filename)
        print(self.test_app.get("/server/command/stop/Really.Cool.Show.mp4"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("Really.Cool.Show.mp4", command.filename)
        print(self.test_app.get("/server/command/stop/Really.Cool.Show%20%20With%20%20Spaces"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("Really.Cool.Show  With  Spaces", command.filename)
