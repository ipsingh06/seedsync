# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json

from controller import ControllerPersist


class TestControllerPersist(unittest.TestCase):
    def test_from_str(self):
        content = """
        {
            "downloaded": ["one", "two", "th ree", "fo.ur"]
        }
        """
        persist = ControllerPersist.from_str(content)
        golden_downloaded = {"one", "two", "th ree", "fo.ur"}
        self.assertEqual(golden_downloaded, persist.downloaded_file_names)

    def test_to_str(self):
        persist = ControllerPersist()
        persist.downloaded_file_names.add("one")
        persist.downloaded_file_names.add("two")
        persist.downloaded_file_names.add("th ree")
        persist.downloaded_file_names.add("fo.ur")
        dct = json.loads(persist.to_str())
        self.assertTrue("downloaded" in dct)
        self.assertEqual({"one", "two", "th ree", "fo.ur"}, set(dct["downloaded"]))
