# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import sys
import copy

from common import overrides
from common import PylftpContext


class TestPylftpContext(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        # Make a copy of the sys argv
        self.sys_argv_orig = copy.deepcopy(sys.argv)

    @overrides(unittest.TestCase)
    def tearDown(self):
        # Restore the original sys argv
        sys.argv = self.sys_argv_orig

    def test_args_config(self):
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config)

        sys.argv = sys.argv[:-4]
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        sys.argv.append("--config")
        sys.argv.append("/path/to/config")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config)

        sys.argv = sys.argv[:-4]
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        with self.assertRaises(SystemExit):
            PylftpContext._parse_args()

    def test_args_patterns(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config)

        sys.argv = sys.argv[:-4]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--patterns")
        sys.argv.append("/path/to/patterns")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config)

        sys.argv = sys.argv[:-4]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        with self.assertRaises(SystemExit):
            PylftpContext._parse_args()

    def test_args_logdir(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        sys.argv.append("--logdir")
        sys.argv.append("/path/to/logdir")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/logdir", args.logdir)

        sys.argv = sys.argv[:-6]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertIsNone(args.logdir)

    def test_args_debug(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        sys.argv.append("-d")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-5]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        sys.argv.append("--debug")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-5]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("-p")
        sys.argv.append("/path/to/patterns")
        args = PylftpContext._parse_args()
        self.assertIsNotNone(args)
        self.assertFalse(args.debug)
