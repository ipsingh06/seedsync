# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile

from common import PylftpConfig, ConfigError
from common.config import PylftpInnerConfig, Checkers, Converters


class TestConverters(unittest.TestCase):
    def test_int(self):
        self.assertEqual(0, Converters.int(None, "", "0"))
        self.assertEqual(1, Converters.int(None, "", "1"))
        self.assertEqual(-1, Converters.int(None, "", "-1"))
        self.assertEqual(5000, Converters.int(None, "", "5000"))
        self.assertEqual(-5000, Converters.int(None, "", "-5000"))
        with self.assertRaises(ConfigError) as e:
            Converters.int(TestConverters, "bad", "")
        self.assertEqual("Bad config: TestConverters.bad is empty", str(e.exception))
        with self.assertRaises(ConfigError) as e:
            Converters.int(TestConverters, "bad", "3.14")
        self.assertEqual("Bad config: TestConverters.bad (3.14) must be an integer value", str(e.exception))
        with self.assertRaises(ConfigError) as e:
            Converters.int(TestConverters, "bad", "cat")
        self.assertEqual("Bad config: TestConverters.bad (cat) must be an integer value", str(e.exception))

    def test_bool(self):
        self.assertEqual(True, Converters.bool(None, "", "True"))
        self.assertEqual(False, Converters.bool(None, "", "False"))
        self.assertEqual(True, Converters.bool(None, "", "1"))
        self.assertEqual(False, Converters.bool(None, "", "0"))
        with self.assertRaises(ConfigError) as e:
            Converters.bool(TestConverters, "bad", "")
        self.assertEqual("Bad config: TestConverters.bad is empty", str(e.exception))
        with self.assertRaises(ConfigError) as e:
            Converters.bool(TestConverters, "bad", "cat")
        self.assertEqual("Bad config: TestConverters.bad (cat) must be a boolean value", str(e.exception))
        with self.assertRaises(ConfigError) as e:
            Converters.bool(TestConverters, "bad", "-3.14")
        self.assertEqual("Bad config: TestConverters.bad (-3.14) must be a boolean value", str(e.exception))


class DummyInnerConfig(PylftpInnerConfig):
    c_prop1 = PylftpInnerConfig._create_property("prop1", Checkers.null, Converters.null)
    a_prop2 = PylftpInnerConfig._create_property("prop2", Checkers.null, Converters.null)
    b_prop3 = PylftpInnerConfig._create_property("prop3", Checkers.null, Converters.null)

    def __init__(self):
        self.c_prop1 = "1"
        self.a_prop2 = "2"
        self.b_prop3 = "3"


class DummyInnerConfig2(PylftpInnerConfig):
    prop_int = PylftpInnerConfig._create_property("prop_int", Checkers.null, Converters.int)
    prop_str = PylftpInnerConfig._create_property("prop_str", Checkers.string_nonempty, Converters.null)

    def __init__(self):
        self.prop_int = None
        self.prop_str = None


class TestPylftpInnerConfig(unittest.TestCase):
    def test_property_order(self):
        dummy_config = DummyInnerConfig()
        self.assertEqual(["c_prop1", "a_prop2", "b_prop3"], list(dummy_config.as_dict().keys()))

    def test_has_property(self):
        dummy_config = DummyInnerConfig()
        self.assertTrue(dummy_config.has_property("c_prop1"))
        self.assertTrue(dummy_config.has_property("a_prop2"))
        self.assertTrue(dummy_config.has_property("b_prop3"))
        self.assertFalse(dummy_config.has_property("not_prop"))
        self.assertFalse(dummy_config.has_property("__init__"))
        self.assertFalse(dummy_config.has_property(""))

    def test_checker_is_called(self):
        dummy_config = DummyInnerConfig2()
        dummy_config.prop_str = "a string"
        self.assertEqual("a string", dummy_config.prop_str)
        with self.assertRaises(ConfigError) as e:
            dummy_config.prop_str = ""
        self.assertEqual("Bad config: DummyInnerConfig2.prop_str is empty", str(e.exception))

    def test_converter_is_called(self):
        dummy_config = DummyInnerConfig2.from_dict({"prop_int": "5", "prop_str": "a"})
        self.assertEqual(5, dummy_config.prop_int)
        with self.assertRaises(ConfigError) as e:
            DummyInnerConfig2.from_dict({"prop_int": "cat", "prop_str": "a"})
        self.assertEqual("Bad config: DummyInnerConfig2.prop_int (cat) must be an integer value", str(e.exception))


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
        bad_dict[key] = "   "
        with self.assertRaises(ConfigError) as error:
            cls.from_dict(bad_dict)
        self.assertTrue(str(error.exception).startswith("Bad config"))

    def check_common(self, cls, good_dict, keys):
        """
        Helper method to run some common checks
        :param cls:
        :param good_dict:
        :param keys:
        :return:
        """
        # unknown
        self.__check_unknown_error(cls, good_dict)

        for key in keys:
            # missing key
            self.__check_missing_error(cls, good_dict, key)
            # empty value
            self.__check_empty_error(cls, good_dict, key)

    def check_bad_value_error(self, cls, good_dict, key, value):
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

    def test_has_section(self):
        config = PylftpConfig()
        self.assertTrue(config.has_section("general"))
        self.assertTrue(config.has_section("lftp"))
        self.assertTrue(config.has_section("controller"))
        self.assertTrue(config.has_section("web"))
        self.assertFalse(config.has_section("nope"))
        self.assertFalse(config.has_section("from_file"))
        self.assertFalse(config.has_section("__init__"))

    def test_general(self):
        good_dict = {
            "debug": "True",
        }
        general = PylftpConfig.General.from_dict(good_dict)
        self.assertEqual(True, general.debug)

        self.check_common(PylftpConfig.General,
                          good_dict,
                          {
                              "debug"
                          })

        # bad values
        self.check_bad_value_error(PylftpConfig.General, good_dict, "debug", "SomeString")
        self.check_bad_value_error(PylftpConfig.General, good_dict, "debug", "-1")

    def test_lftp(self):
        good_dict = {
            "remote_address": "remote.server.com",
            "remote_username": "remote-user",
            "remote_path": "/path/on/remote/server",
            "local_path": "/path/on/local/server",
            "remote_path_to_scan_script": "/path/on/remote/server/to/scan/script",
            "num_max_parallel_downloads": "2",
            "num_max_parallel_files_per_download": "3",
            "num_max_connections_per_root_file": "4",
            "num_max_connections_per_dir_file": "6",
            "num_max_total_connections": "7"
        }
        lftp = PylftpConfig.Lftp.from_dict(good_dict)
        self.assertEqual("remote.server.com", lftp.remote_address)
        self.assertEqual("remote-user", lftp.remote_username)
        self.assertEqual("/path/on/remote/server", lftp.remote_path)
        self.assertEqual("/path/on/local/server", lftp.local_path)
        self.assertEqual("/path/on/remote/server/to/scan/script", lftp.remote_path_to_scan_script)
        self.assertEqual(2, lftp.num_max_parallel_downloads)
        self.assertEqual(3, lftp.num_max_parallel_files_per_download)
        self.assertEqual(4, lftp.num_max_connections_per_root_file)
        self.assertEqual(6, lftp.num_max_connections_per_dir_file)
        self.assertEqual(7, lftp.num_max_total_connections)

        self.check_common(PylftpConfig.Lftp,
                          good_dict,
                          {
                              "remote_address",
                              "remote_username",
                              "remote_path",
                              "local_path",
                              "remote_path_to_scan_script",
                              "num_max_parallel_downloads",
                              "num_max_parallel_files_per_download",
                              "num_max_connections_per_root_file",
                              "num_max_connections_per_dir_file",
                              "num_max_total_connections"
                          })

        # bad values
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads", "-1")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_downloads", "0")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download", "-1")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_parallel_files_per_download", "0")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_root_file", "-1")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_root_file", "0")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_dir_file", "-1")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_connections_per_dir_file", "0")
        self.check_bad_value_error(PylftpConfig.Lftp, good_dict, "num_max_total_connections", "-1")

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

        self.check_common(PylftpConfig.Controller,
                          good_dict,
                          {
                              "interval_ms_remote_scan",
                              "interval_ms_local_scan",
                              "interval_ms_downloading_scan"
                          })

        # bad values
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan", "-1")
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_remote_scan", "0")
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan", "-1")
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_local_scan", "0")
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_downloading_scan", "-1")
        self.check_bad_value_error(PylftpConfig.Controller, good_dict, "interval_ms_downloading_scan", "0")

    def test_web(self):
        good_dict = {
            "port": "1234",
        }
        web = PylftpConfig.Web.from_dict(good_dict)
        self.assertEqual(1234, web.port)

        self.check_common(PylftpConfig.Web,
                          good_dict,
                          {
                              "port"
                          })

        # bad values
        self.check_bad_value_error(PylftpConfig.Web, good_dict, "port", "-1")
        self.check_bad_value_error(PylftpConfig.Web, good_dict, "port", "0")

    def test_from_file(self):
        # Create empty config file
        config_file = open(tempfile.mktemp(suffix="test_config"), "w")

        config_file.write("""
        [General]
        debug=False

        [Lftp]
        remote_address=remote.server.com
        remote_username=remote-user
        remote_path=/path/on/remote/server
        local_path=/path/on/local/server
        remote_path_to_scan_script=/path/on/remote/server/to/scan/script
        num_max_parallel_downloads=2
        num_max_parallel_files_per_download=3
        num_max_connections_per_root_file=4
        num_max_connections_per_dir_file=5
        num_max_total_connections=7

        [Controller]
        interval_ms_remote_scan=30000
        interval_ms_local_scan=10000
        interval_ms_downloading_scan=2000

        [Web]
        port=88
        """)
        config_file.flush()
        config = PylftpConfig.from_file(config_file.name)

        self.assertEqual(False, config.general.debug)

        self.assertEqual("remote.server.com", config.lftp.remote_address)
        self.assertEqual("remote-user", config.lftp.remote_username)
        self.assertEqual("/path/on/remote/server", config.lftp.remote_path)
        self.assertEqual("/path/on/local/server", config.lftp.local_path)
        self.assertEqual("/path/on/remote/server/to/scan/script", config.lftp.remote_path_to_scan_script)
        self.assertEqual(2, config.lftp.num_max_parallel_downloads)
        self.assertEqual(3, config.lftp.num_max_parallel_files_per_download)
        self.assertEqual(4, config.lftp.num_max_connections_per_root_file)
        self.assertEqual(5, config.lftp.num_max_connections_per_dir_file)
        self.assertEqual(7, config.lftp.num_max_total_connections)

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
        config.general.debug = True
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
        config.controller.interval_ms_remote_scan = 1234
        config.controller.interval_ms_local_scan = 5678
        config.controller.interval_ms_downloading_scan = 9012
        config.web.port = 13
        config.to_file(config_file_path)
        with open(config_file_path, "r") as f:
            actual_str = f.read()
        print(actual_str)

        golden_str = """
        [General]
        debug = True

        [Lftp]
        remote_address = server.remote.com
        remote_username = user-on-remote-server
        remote_path = /remote/server/path
        local_path = /local/server/path
        remote_path_to_scan_script = /remote/server/path/to/script
        num_max_parallel_downloads = 6
        num_max_parallel_files_per_download = 7
        num_max_connections_per_root_file = 2
        num_max_connections_per_dir_file = 3
        num_max_total_connections = 4

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
        for i, _ in enumerate(golden_lines):
            self.assertEqual(golden_lines[i], actual_lines[i])
