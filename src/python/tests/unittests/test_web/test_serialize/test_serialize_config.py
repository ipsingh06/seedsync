# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json

from common import Config
from web.serialize import SerializeConfig


class TestSerializeConfig(unittest.TestCase):
    def test_section_general(self):
        config = Config()
        config.general.debug = True
        out = SerializeConfig.config(config)
        out_dict = json.loads(out)
        self.assertIn("general", out_dict)
        self.assertEqual(True, out_dict["general"]["debug"])

    def test_section_lftp(self):
        config = Config()
        config.lftp.remote_address = "server.remote.com"
        config.lftp.remote_username = "user-on-remote-server"
        config.lftp.remote_path = "/remote/server/path"
        config.lftp.local_path = "/local/server/path"
        config.lftp.remote_path_to_scan_script = "/remote/server/path/to/script"
        config.lftp.num_max_parallel_downloads = 6
        config.lftp.num_max_parallel_files_per_download = 7
        config.lftp.num_max_connections_per_root_file = 2
        config.lftp.num_max_connections_per_dir_file = 3
        config.lftp.num_max_total_connections = 4
        out = SerializeConfig.config(config)
        out_dict = json.loads(out)
        self.assertIn("lftp", out_dict)
        self.assertEqual("server.remote.com", out_dict["lftp"]["remote_address"])
        self.assertEqual("user-on-remote-server", out_dict["lftp"]["remote_username"])
        self.assertEqual("/remote/server/path", out_dict["lftp"]["remote_path"])
        self.assertEqual("/local/server/path", out_dict["lftp"]["local_path"])
        self.assertEqual("/remote/server/path/to/script", out_dict["lftp"]["remote_path_to_scan_script"])
        self.assertEqual(6, out_dict["lftp"]["num_max_parallel_downloads"])
        self.assertEqual(7, out_dict["lftp"]["num_max_parallel_files_per_download"])
        self.assertEqual(2, out_dict["lftp"]["num_max_connections_per_root_file"])
        self.assertEqual(3, out_dict["lftp"]["num_max_connections_per_dir_file"])
        self.assertEqual(4, out_dict["lftp"]["num_max_total_connections"])

    def test_section_controller(self):
        config = Config()
        config.controller.interval_ms_remote_scan = 1234
        config.controller.interval_ms_local_scan = 5678
        config.controller.interval_ms_downloading_scan = 9012
        out = SerializeConfig.config(config)
        out_dict = json.loads(out)
        self.assertIn("controller", out_dict)
        self.assertEqual(1234, out_dict["controller"]["interval_ms_remote_scan"])
        self.assertEqual(5678, out_dict["controller"]["interval_ms_local_scan"])
        self.assertEqual(9012, out_dict["controller"]["interval_ms_downloading_scan"])

    def test_section_web(self):
        config = Config()
        config.web.port = 8080
        out = SerializeConfig.config(config)
        out_dict = json.loads(out)
        self.assertIn("web", out_dict)
        self.assertEqual(8080, out_dict["web"]["port"])
