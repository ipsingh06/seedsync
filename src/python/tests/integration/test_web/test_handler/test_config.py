# Copyright 2017, Inderpreet Singh, All rights reserved.

import json
from urllib.parse import quote

from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestConfigHandler(BaseTestWebApp):
    def test_get(self):
        self.context.config.general.debug = True
        self.context.config.lftp.remote_path = "/remote/server/path"
        self.context.config.controller.interval_ms_local_scan = 5678
        self.context.config.web.port = 8080
        resp = self.test_app.get("/server/config/get")
        self.assertEqual(200, resp.status_int)
        json_dict = json.loads(str(resp.html))
        self.assertEqual(True, json_dict["general"]["debug"])
        self.assertEqual("/remote/server/path", json_dict["lftp"]["remote_path"])
        self.assertEqual(5678, json_dict["controller"]["interval_ms_local_scan"])
        self.assertEqual(8080, json_dict["web"]["port"])

    def test_set_good(self):
        self.assertEqual(None, self.context.config.general.debug)
        resp = self.test_app.get("/server/config/set/general/debug/True")
        self.assertEqual(200, resp.status_int)
        self.assertEqual(True, self.context.config.general.debug)

        self.assertEqual(None, self.context.config.lftp.remote_path)
        uri = quote(quote("/path/to/somewhere", safe=""), safe="")
        resp = self.test_app.get("/server/config/set/lftp/remote_path/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual("/path/to/somewhere", self.context.config.lftp.remote_path)

        self.assertEqual(None, self.context.config.controller.interval_ms_local_scan)
        resp = self.test_app.get("/server/config/set/controller/interval_ms_local_scan/5678")
        self.assertEqual(200, resp.status_int)
        self.assertEqual(5678, self.context.config.controller.interval_ms_local_scan)

        self.assertEqual(None, self.context.config.web.port)
        resp = self.test_app.get("/server/config/set/web/port/8080")
        self.assertEqual(200, resp.status_int)
        self.assertEqual(8080, self.context.config.web.port)

    def test_set_missing_section(self):
        self.assertFalse(self.context.config.has_section("bad_section"))
        resp = self.test_app.get("/server/config/set/bad_section/option/value", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("There is no section 'bad_section' in config", str(resp.html))
        self.assertFalse(self.context.config.has_section("bad_section"))

    def test_set_missing_option(self):
        self.assertFalse(self.context.config.general.has_property("bad_option"))
        resp = self.test_app.get("/server/config/set/general/bad_option/value", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Section 'general' in config has no option 'bad_option'", str(resp.html))
        self.assertFalse(self.context.config.general.has_property("bad_option"))

    def test_set_bad_value(self):
        # boolean
        self.assertEqual(None, self.context.config.general.debug)
        resp = self.test_app.get("/server/config/set/general/debug/cat", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Bad config: General.debug (cat) must be a boolean value", str(resp.html))
        self.assertEqual(None, self.context.config.general.debug)

        # positive int
        self.assertEqual(None, self.context.config.controller.interval_ms_local_scan)
        resp = self.test_app.get("/server/config/set/controller/interval_ms_local_scan/-1", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Bad config: Controller.interval_ms_local_scan (-1) must be greater than 0", str(resp.html))
        self.assertEqual(None, self.context.config.controller.interval_ms_local_scan)

    def test_set_empty_value(self):
        self.assertEqual(None, self.context.config.lftp.remote_path)
        resp = self.test_app.get("/server/config/set/lftp/remote_path/", expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(None, self.context.config.lftp.remote_path)

        self.assertEqual(None, self.context.config.lftp.remote_path)
        resp = self.test_app.get("/server/config/set/lftp/remote_path/%20%20", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Bad config: Lftp.remote_path is empty", str(resp.html))
        self.assertEqual(None, self.context.config.lftp.remote_path)
