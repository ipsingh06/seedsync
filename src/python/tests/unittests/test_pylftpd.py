# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import sys
import copy

from common import overrides
from pylftpd import Pylftpd


class TestPylftpd(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        # Make a copy of the sys argv
        self.sys_argv_orig = copy.deepcopy(sys.argv)

    @overrides(unittest.TestCase)
    def tearDown(self):
        # Restore the original sys argv
        sys.argv = self.sys_argv_orig

    def test_args_config(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config_dir)

        sys.argv = sys.argv[:-6]
        sys.argv.append("--config_dir")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config_dir)

        sys.argv = sys.argv[:-6]
        with self.assertRaises(SystemExit):
            Pylftpd._parse_args()

    def test_args_html(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/html", args.html)

    def test_args_scanfs(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/scanfs", args.scanfs)

    def test_args_logdir(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--logdir")
        sys.argv.append("/path/to/logdir")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/logdir", args.logdir)

        sys.argv = sys.argv[:-8]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertIsNone(args.logdir)

    def test_args_debug(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        sys.argv.append("-d")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-7]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--debug")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-7]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Pylftpd._parse_args()
        self.assertIsNotNone(args)
        self.assertFalse(args.debug)
