# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json

from controller import AutoQueuePattern
from web.serialize import SerializeAutoQueue


class TestSerializeConfig(unittest.TestCase):
    def test_is_list(self):
        patterns = [
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="two"),
            AutoQueuePattern(pattern="three")
        ]
        out = SerializeAutoQueue.patterns(patterns)
        out_list = json.loads(out)
        self.assertIsInstance(out_list, list)
        self.assertEqual(3, len(out_list))

    def test_patterns(self):
        patterns = [
            AutoQueuePattern(pattern="one"),
            AutoQueuePattern(pattern="tw o"),
            AutoQueuePattern(pattern="th'ree"),
            AutoQueuePattern(pattern="fo\"ur"),
            AutoQueuePattern(pattern="fi=ve")
        ]
        out = SerializeAutoQueue.patterns(patterns)
        out_list = json.loads(out)
        self.assertEqual(5, len(out_list))
        self.assertEqual([
            {"pattern": "one"},
            {"pattern": "tw o"},
            {"pattern": "th'ree"},
            {"pattern": "fo\"ur"},
            {"pattern": "fi=ve"},
        ], out_list)
