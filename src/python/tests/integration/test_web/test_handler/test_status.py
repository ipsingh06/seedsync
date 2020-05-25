# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestStatusHandler(BaseTestWebApp):
    def test_status(self):
        resp = self.test_app.get("/server/status")
        self.assertEqual(200, resp.status_int)
        json_dict = json.loads(str(resp.html))
        self.assertEqual(True, json_dict["server"]["up"])
