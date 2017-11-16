# Copyright 2017, Inderpreet Singh, All rights reserved.

from unittest.mock import MagicMock

from tests.integration.test_web.test_web_app import BaseTestWebApp
from controller import Controller


class TestControllerActionHandler(BaseTestWebApp):
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
