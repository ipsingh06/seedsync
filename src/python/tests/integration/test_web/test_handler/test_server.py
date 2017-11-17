# Copyright 2017, Inderpreet Singh, All rights reserved.

from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestServerHandler(BaseTestWebApp):
    def test_restart(self):
        self.assertFalse(self.web_app_builder.server_handler.is_restart_requested())
        print(self.test_app.get("/server/command/restart"))
        self.assertTrue(self.web_app_builder.server_handler.is_restart_requested())
        print(self.test_app.get("/server/command/restart"))
        self.assertTrue(self.web_app_builder.server_handler.is_restart_requested())
