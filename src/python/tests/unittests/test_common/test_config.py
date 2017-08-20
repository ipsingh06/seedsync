# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile

from common import PylftpConfig, PylftpError, overrides


class TestPylftpConfig(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        # Create empty config file
        self.config_file = open(tempfile.mktemp(suffix="test_config"), "w")

    @overrides(unittest.TestCase)
    def tearDown(self):
        # Remove config file
        self.config_file.close()
        os.remove(self.config_file.name)

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
        with self.assertRaises(PylftpError) as error:
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
        with self.assertRaises(PylftpError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Missing config"))

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
        with self.assertRaises(PylftpError) as error:
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

        # bad values
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads", "-1")
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download", "-1")
        self.__check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_file", "-1")

    def test_controller(self):
        good_dict = {
            "interval_ms_remote_scan": "30000",
            "interval_ms_local_scan": "10000",
        }
        lftp = PylftpConfig.Controller.from_dict(good_dict)
        self.assertEqual(30000, lftp.interval_ms_remote_scan)
        self.assertEqual(10000, lftp.interval_ms_local_scan)

        # unknown
        self.__check_unknown_error(PylftpConfig.Controller, good_dict)

        # missing keys
        self.__check_missing_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan")
        self.__check_missing_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan")

        # bad values
        self.__check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan", "-1")
        self.__check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan", "-1")

    def test_from_file(self):
        self.config_file.write("""
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
        """)
        self.config_file.flush()
        config = PylftpConfig.from_file(self.config_file.name)
        self.assertEqual("remote.server.com", config.lftp.remote_address)
        self.assertEqual("remote-user", config.lftp.remote_username)
        self.assertEqual("/path/on/remote/server", config.lftp.remote_path)
        self.assertEqual("/path/on/local/server", config.lftp.local_path)
        self.assertEqual("/path/on/remote/server/to/scan/script", config.lftp.remote_path_to_scan_script)
        self.assertEqual(2, config.lftp.num_max_parallel_downloads)
        self.assertEqual(3, config.lftp.num_max_parallel_files_per_download)
        self.assertEqual(4, config.lftp.num_max_connections_per_file)

        # unknown section error
        self.config_file.write("""
        [Unknown]
        key=value
        """)
        self.config_file.flush()
        with self.assertRaises(PylftpError) as error:
            PylftpConfig.from_file(self.config_file.name)
        self.assertTrue(str(error.exception).startswith("Unknown section"))
