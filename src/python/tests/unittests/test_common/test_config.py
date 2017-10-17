# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile

from common import PylftpConfig, ConfigError, overrides


class TestPylftpConfig(unittest.TestCase):
    def __check_unknown_error(self, cls, good_dict):
        """
        Helper method to check that a config class raises an error on
        an unknown key
        :param cls:
        :param good_dict:
        :return:
        """
        bad_dict = dict(good_dict)
        bad_dict["unknown"] = "how did this get here"
        with self.assertRaises(ConfigError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Unknown config"))

    def __check_missing_error(self, cls, good_dict, key):
        """
        Helper method to check that a config class raises an error on
        a missing key
        :param cls:
        :param good_dict:
        :param key:
        :return:
        """
        bad_dict = dict(good_dict)
        del bad_dict[key]
        with self.assertRaises(ConfigError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Missing config"))

    def __check_empty_error(self, cls, good_dict, key):
        """
        Helper method to check that a config class raises an error on
        a empty value
        :param cls:
        :param good_dict:
        :param key:
        :return:
        """
        bad_dict = dict(good_dict)
        bad_dict[key] = ""
        with self.assertRaises(ConfigError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Bad config"))

    def __check_bad_value_error(self, cls, good_dict, key, value):
        """
        Helper method to check that a config class raises an error on
        a bad value
        :param cls:
        :param good_dict:
        :param key:
        :param value:
        :return:
        """
        bad_dict = dict(good_dict)
        bad_dict[key] = value
        with self.assertRaises(ConfigError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Bad config"))

    def test_lftp(self):
        good_dict = {
            "remote_address": "remote.server.com",
            "remote_username": "remote-user",
            "remote_path": "/path/on/remote/server",
            "local_path": "/path/on/local/server",
            "remote_path_to_scan_script": "/path/on/remote/server/to/scan/script",
            "num_max_parallel_downloads": "2",
            "num_max_parallel_files_per_download": "3",
            "num_max_connections_per_file": "4",
        }
        lftp = PylftpConfig.Lftp.from_dict(good_dict)
        self.assertEqual("remote.server.com", lftp.remote_address)
        self.assertEqual("remote-user", lftp.remote_username)
        self.assertEqual("/path/on/remote/server", lftp.remote_path)
        self.assertEqual("/path/on/local/server", lftp.local_path)
        self.assertEqual("/path/on/remote/server/to/scan/script", lftp.remote_path_to_scan_script)
        self.assertEqual(2, lftp.num_max_parallel_downloads)
        self.assertEqual(3, lftp.num_max_parallel_files_per_download)
        self.assertEqual(4, lftp.num_max_connections_per_file)

        # unknown
        self.__check_unknown_error(PylftpConfig.Lftp, good_dict)

        # missing keys
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "remote_address")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "remote_username")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "remote_path")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "local_path")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "remote_path_to_scan_script")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download")
        self.__check_missing_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_file")

        # empty values
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "remote_address")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "remote_username")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "remote_path")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "local_path")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "remote_path_to_scan_script")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download")
        self.__check_empty_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_file")

        # bad values
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads", "-1")
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download", "-1")
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_file", "-1")

    def test_controller(self):
        good_dict = {
            "interval_ms_remote_scan": "30000",
            "interval_ms_local_scan": "10000",
            "interval_ms_downloading_scan": "2000",
        }
        lftp = PylftpConfig.Controller.from_dict(good_dict)
        self.assertEqual(30000, lftp.interval_ms_remote_scan)
        self.assertEqual(10000, lftp.interval_ms_local_scan)
        self.assertEqual(2000, lftp.interval_ms_downloading_scan)

        # unknown
        self.__check_unknown_error(PylftpConfig.Controller, good_dict)

        # missing keys
        self.__check_missing_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan")
        self.__check_missing_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan")
        self.__check_missing_error(PylftpConfig.Controller, good_dict, "interval_ms_downloading_scan")

        # empty values
        self.__check_empty_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan")
        self.__check_empty_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan")
        self.__check_empty_error(PylftpConfig.Controller, good_dict, "interval_ms_downloading_scan")

        # bad values
        self.__check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan", "-1")
        self.__check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan", "-1")
        self.__check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_downloading_scan", "-1")

    def test_web(self):
        good_dict = {
            "port": "1234",
        }
        web = PylftpConfig.Web.from_dict(good_dict)
        self.assertEqual(1234, web.port)

        # unknown
        self.__check_unknown_error(PylftpConfig.Web, good_dict)

        # missing keys
        self.__check_missing_error(PylftpConfig.Web, good_dict, "port")

        # empty values
        self.__check_empty_error(PylftpConfig.Web, good_dict, "port")

        # bad values
        self.__check_bad_value_error(PylftpConfig.Web, good_dict, "port", "-1")

    def test_from_file(self):
        # Create empty config file
        config_file = open(tempfile.mktemp(suffix="test_config"), "w")

        config_file.write("""
        [Lftp]
        remote_address=remote.server.com
        remote_username=remote-user
        remote_path=/path/on/remote/server
        local_path=/path/on/local/server
        remote_path_to_scan_script=/path/on/remote/server/to/scan/script
        num_max_parallel_downloads=2
        num_max_parallel_files_per_download=3
        num_max_connections_per_file=4

        [Controller]
        interval_ms_remote_scan=30000
        interval_ms_local_scan=10000
        interval_ms_downloading_scan=2000

        [Web]
        port=88
        """)
        config_file.flush()
        config = PylftpConfig.from_file(config_file.name)

        self.assertEqual("remote.server.com", config.lftp.remote_address)
        self.assertEqual("remote-user", config.lftp.remote_username)
        self.assertEqual("/path/on/remote/server", config.lftp.remote_path)
        self.assertEqual("/path/on/local/server", config.lftp.local_path)
        self.assertEqual("/path/on/remote/server/to/scan/script", config.lftp.remote_path_to_scan_script)
        self.assertEqual(2, config.lftp.num_max_parallel_downloads)
        self.assertEqual(3, config.lftp.num_max_parallel_files_per_download)
        self.assertEqual(4, config.lftp.num_max_connections_per_file)

        self.assertEqual(30000, config.controller.interval_ms_remote_scan)
        self.assertEqual(10000, config.controller.interval_ms_local_scan)
        self.assertEqual(2000, config.controller.interval_ms_downloading_scan)

        self.assertEqual(88, config.web.port)

        # unknown section error
        config_file.write("""
        [Unknown]
        key=value
        """)
        config_file.flush()
        with self.assertRaises(ConfigError) as error:
            PylftpConfig.from_file(config_file.name)
        self.assertTrue(str(error.exception).startswith("Unknown section"))

        # Remove config file
        config_file.close()
        os.remove(config_file.name)

    def test_to_file(self):
        config_file_path = tempfile.mktemp(suffix="test_config")

        config = PylftpConfig()
        config.lftp.remote_address = "server.remote.com"
        config.lftp.remote_username = "user-on-remote-server"
        config.lftp.remote_path = "/remote/server/path"
        config.lftp.local_path = "/local/server/path"
        config.lftp.remote_path_to_scan_script = "/remote/server/path/to/script"
        config.lftp.num_max_parallel_downloads = 6
        config.lftp.num_max_parallel_files_per_download = 7
        config.lftp.num_max_connections_per_file = 8
        config.controller.interval_ms_remote_scan = 1234
        config.controller.interval_ms_local_scan = 5678
        config.controller.interval_ms_downloading_scan = 9012
        config.web.port = 13
        config.to_file(config_file_path)
        with open(config_file_path, "r") as f:
            actual_str = f.read()

        golden_str = """
        [Lftp]
        remote_address = server.remote.com
        remote_username = user-on-remote-server
        remote_path = /remote/server/path
        local_path = /local/server/path
        remote_path_to_scan_script = /remote/server/path/to/script
        num_max_parallel_downloads = 6
        num_max_parallel_files_per_download = 7
        num_max_connections_per_file = 8

        [Controller]
        interval_ms_remote_scan = 1234
        interval_ms_local_scan = 5678
        interval_ms_downloading_scan = 9012

        [Web]
        port = 13
        """

        golden_lines = [s.strip() for s in golden_str.splitlines()]
        golden_lines = list(filter(None, golden_lines))  # remove blank lines
        actual_lines = [s.strip() for s in actual_str.splitlines()]
        actual_lines = list(filter(None, actual_lines))  # remove blank lines

        self.assertEqual(len(golden_lines), len(actual_lines))
        for i,_ in enumerate(golden_lines):
            self.assertEqual(golden_lines[i], actual_lines[i])
