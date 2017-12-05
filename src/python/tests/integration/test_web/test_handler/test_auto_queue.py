# Copyright 2017, Inderpreet Singh, All rights reserved.

import json
from urllib.parse import quote

from controller import AutoQueuePattern
from tests.integration.test_web.test_web_app import BaseTestWebApp


class TestAutoQueueHandler(BaseTestWebApp):
    def test_get(self):
        self.auto_queue_persist.add_pattern(AutoQueuePattern(pattern="one"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern(pattern="t wo"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern(pattern="thr'ee"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern(pattern="fo\"ur"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern(pattern="fi%ve"))
        resp = self.test_app.get("/server/autoqueue/get")
        self.assertEqual(200, resp.status_int)
        json_list = json.loads(str(resp.html))
        self.assertEqual(5, len(json_list))
        self.assertIn({"pattern": "one"}, json_list)
        self.assertIn({"pattern": "t wo"}, json_list)
        self.assertIn({"pattern": "thr'ee"}, json_list)
        self.assertIn({"pattern": "fo\"ur"}, json_list)
        self.assertIn({"pattern": "fi%ve"}, json_list)

    def test_add_good(self):
        resp = self.test_app.get("/server/autoqueue/add/one")
        self.assertEqual(200, resp.status_int)
        self.assertEqual(1, len(self.auto_queue_persist.patterns))
        self.assertIn(AutoQueuePattern("one"), self.auto_queue_persist.patterns)

        uri = quote(quote("/value/with/slashes", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/add/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(2, len(self.auto_queue_persist.patterns))
        self.assertIn(AutoQueuePattern("/value/with/slashes"), self.auto_queue_persist.patterns)

        uri = quote(quote(" value with spaces", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/add/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(3, len(self.auto_queue_persist.patterns))
        self.assertIn(AutoQueuePattern(" value with spaces"), self.auto_queue_persist.patterns)

        uri = quote(quote("value'with'singlequote", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/add/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(4, len(self.auto_queue_persist.patterns))
        self.assertIn(AutoQueuePattern("value'with'singlequote"), self.auto_queue_persist.patterns)

        uri = quote(quote("value\"with\"doublequote", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/add/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(5, len(self.auto_queue_persist.patterns))
        self.assertIn(AutoQueuePattern("value\"with\"doublequote"), self.auto_queue_persist.patterns)

    def test_add_double(self):
        resp = self.test_app.get("/server/autoqueue/add/one")
        self.assertEqual(200, resp.status_int)
        resp = self.test_app.get("/server/autoqueue/add/one", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Auto-queue pattern 'one' already exists.", str(resp.html))

    def test_add_empty_value(self):
        uri = quote(quote("  ", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/add/" + uri, expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual(0, len(self.auto_queue_persist.patterns))

        resp = self.test_app.get("/server/autoqueue/add/", expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(0, len(self.auto_queue_persist.patterns))

    def test_remove_good(self):
        self.auto_queue_persist.add_pattern(AutoQueuePattern("one"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern("/value/with/slashes"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern(" value with spaces"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern("value'with'singlequote"))
        self.auto_queue_persist.add_pattern(AutoQueuePattern("value\"with\"doublequote"))

        resp = self.test_app.get("/server/autoqueue/remove/one")
        self.assertEqual(200, resp.status_int)
        self.assertEqual(4, len(self.auto_queue_persist.patterns))
        self.assertNotIn(AutoQueuePattern("one"), self.auto_queue_persist.patterns)

        uri = quote(quote("/value/with/slashes", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/remove/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(3, len(self.auto_queue_persist.patterns))
        self.assertNotIn(AutoQueuePattern("/value/with/slashes"), self.auto_queue_persist.patterns)

        uri = quote(quote(" value with spaces", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/remove/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(2, len(self.auto_queue_persist.patterns))
        self.assertNotIn(AutoQueuePattern(" value with spaces"), self.auto_queue_persist.patterns)

        uri = quote(quote("value'with'singlequote", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/remove/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(1, len(self.auto_queue_persist.patterns))
        self.assertNotIn(AutoQueuePattern("value'with'singlequote"), self.auto_queue_persist.patterns)

        uri = quote(quote("value\"with\"doublequote", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/remove/" + uri)
        self.assertEqual(200, resp.status_int)
        self.assertEqual(0, len(self.auto_queue_persist.patterns))
        self.assertNotIn(AutoQueuePattern("value\"with\"doublequote"), self.auto_queue_persist.patterns)

    def test_remove_non_existing(self):
        resp = self.test_app.get("/server/autoqueue/remove/one", expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Auto-queue pattern 'one' doesn't exist.", str(resp.html))

    def test_remove_empty_value(self):
        uri = quote(quote("  ", safe=""), safe="")
        resp = self.test_app.get("/server/autoqueue/remove/" + uri, expect_errors=True)
        self.assertEqual(400, resp.status_int)
        self.assertEqual("Auto-queue pattern '  ' doesn't exist.", str(resp.html))
        self.assertEqual(0, len(self.auto_queue_persist.patterns))

        resp = self.test_app.get("/server/autoqueue/remove/", expect_errors=True)
        self.assertEqual(404, resp.status_int)
        self.assertEqual(0, len(self.auto_queue_persist.patterns))
