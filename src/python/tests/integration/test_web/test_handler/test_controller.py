# Copyright 2017, Inderpreet Singh, All rights reserved.

from unittest.mock import MagicMock
from urllib.parse import quote

from tests.integration.test_web.test_web_app import BaseTestWebApp
from controller import Controller


class TestControllerHandler(BaseTestWebApp):
    def test_queue(self):
        def side_effect(cmd: Controller.Command):
            cmd.callbacks[0].on_success()
        self.controller.queue_command = MagicMock()
        self.controller.queue_command.side_effect = side_effect

        print(self.test_app.get("/server/command/queue/test1"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("test1", command.filename)

        uri = quote(quote("/value/with/slashes", safe=""), safe="")
        print(self.test_app.get("/server/command/queue/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("/value/with/slashes", command.filename)

        uri = quote(quote(" value with spaces", safe=""), safe="")
        print(self.test_app.get("/server/command/queue/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual(" value with spaces", command.filename)

        uri = quote(quote("value'with'singlequote", safe=""), safe="")
        print(self.test_app.get("/server/command/queue/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("value'with'singlequote", command.filename)

        uri = quote(quote("value\"with\"doublequote", safe=""), safe="")
        print(self.test_app.get("/server/command/queue/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.QUEUE, command.action)
        self.assertEqual("value\"with\"doublequote", command.filename)

    def test_stop(self):
        def side_effect(cmd: Controller.Command):
            cmd.callbacks[0].on_success()
        self.controller.queue_command = MagicMock()
        self.controller.queue_command.side_effect = side_effect

        print(self.test_app.get("/server/command/stop/test1"))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("test1", command.filename)

        uri = quote(quote("/value/with/slashes", safe=""), safe="")
        print(self.test_app.get("/server/command/stop/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("/value/with/slashes", command.filename)

        uri = quote(quote(" value with spaces", safe=""), safe="")
        print(self.test_app.get("/server/command/stop/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual(" value with spaces", command.filename)

        uri = quote(quote("value'with'singlequote", safe=""), safe="")
        print(self.test_app.get("/server/command/stop/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("value'with'singlequote", command.filename)

        uri = quote(quote("value\"with\"doublequote", safe=""), safe="")
        print(self.test_app.get("/server/command/stop/"+uri))
        command = self.controller.queue_command.call_args[0][0]
        self.assertEqual(Controller.Command.Action.STOP, command.action)
        self.assertEqual("value\"with\"doublequote", command.filename)
