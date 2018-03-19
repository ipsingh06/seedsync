# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile
import shutil
import filecmp
import logging
import sys

import timeout_decorator
from parameterized import parameterized

from common import overrides
from ssh import Sshcp, SshcpError


# This is outside so it can be used in the parameterized decorators
# noinspection SpellCheckingInspection
_PASSWORD = "seedsyncpass"
# noinspection SpellCheckingInspection
_PARAMS = [
    ("password", _PASSWORD),
    ("keyauth", None)
]


# noinspection SpellCheckingInspection
class TestSshcp(unittest.TestCase):
    __KEEP_FILES = False  # for debugging

    @overrides(unittest.TestCase)
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sshcp")
        self.local_dir = os.path.join(self.temp_dir, "local")
        os.mkdir(self.local_dir)
        self.remote_dir = os.path.join(self.temp_dir, "remote")
        os.mkdir(self.remote_dir)
        # Allow group access for the seedsynctest account
        os.chmod(self.temp_dir, 0o770)

        # Note: seedsynctest account must be set up. See DeveloperReadme.md for details
        self.host = "localhost"
        self.port = 22
        self.user = "seedsynctest"

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)

        # Create local file
        self.local_file = os.path.join(self.local_dir, "file.txt")
        self.remote_file = os.path.join(self.remote_dir, "file2.txt")
        with open(self.local_file, "w") as f:
            f.write("this is a test file")

    @overrides(unittest.TestCase)
    def tearDown(self):
        if not self.__KEEP_FILES:
            shutil.rmtree(self.temp_dir)

    def test_ctor(self):
        sshcp = Sshcp(host=self.host, port=self.port)
        self.assertIsNotNone(sshcp)

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_copy(self, _, password):
        self.assertFalse(os.path.exists(self.remote_file))
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)
        sshcp.copy(local_path=self.local_file, remote_path=self.remote_file)

        self.assertTrue(filecmp.cmp(self.local_file, self.remote_file))

    @timeout_decorator.timeout(5)
    def test_copy_error_bad_password(self):
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password="wrong password")
        with self.assertRaises(SshcpError) as ctx:
            sshcp.copy(local_path=self.local_file, remote_path=self.remote_file)
        self.assertEqual("Incorrect password", str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_copy_error_missing_local_file(self, _, password):
        local_file = os.path.join(self.local_dir, "nofile.txt")
        self.assertFalse(os.path.exists(self.remote_file))
        self.assertFalse(os.path.exists(local_file))

        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)
        with self.assertRaises(SshcpError) as ctx:
            sshcp.copy(local_path=local_file, remote_path=self.remote_file)
        self.assertTrue("No such file or directory" in str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_copy_error_missing_remote_dir(self, _, password):
        remote_file = os.path.join(self.remote_dir, "nodir", "file2.txt")
        self.assertFalse(os.path.exists(remote_file))

        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)
        with self.assertRaises(SshcpError) as ctx:
            sshcp.copy(local_path=self.local_file, remote_path=remote_file)
        self.assertTrue("No such file or directory" in str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_copy_error_bad_host(self, _, password):
        sshcp = Sshcp(host="badhost", port=self.port, user=self.user, password=password)
        with self.assertRaises(SshcpError) as ctx:
            sshcp.copy(local_path=self.local_file, remote_path=self.remote_file)
        self.assertTrue("Bad hostname" in str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_shell(self, _, password):
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)
        out = sshcp.shell("cd {}; pwd".format(self.local_dir))
        out_str = out.decode().strip()
        self.assertEqual(self.local_dir, out_str)

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_shell_with_escape_characters(self, _, password):
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)

        # single quotes
        _dir = os.path.join(self.remote_dir, "a a")
        out = sshcp.shell("mkdir '{}' && cd '{}' && pwd".format(_dir, _dir))
        out_str = out.decode().strip()
        self.assertEqual(_dir, out_str)

        # double quotes
        _dir = os.path.join(self.remote_dir, "a b")
        out = sshcp.shell('mkdir "{}" && cd "{}" && pwd'.format(_dir, _dir))
        out_str = out.decode().strip()
        self.assertEqual(_dir, out_str)

        # single and double quotes - error out
        _dir = os.path.join(self.remote_dir, "a b")
        with self.assertRaises(ValueError):
            sshcp.shell('mkdir "{}" && cd \'{}\' && pwd'.format(_dir, _dir))

    @timeout_decorator.timeout(5)
    def test_shell_error_bad_password(self):
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password="wrong password")
        with self.assertRaises(SshcpError) as ctx:
            sshcp.shell("cd {}; pwd".format(self.local_dir))
        self.assertEqual("Incorrect password", str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_shell_error_bad_host(self, _, password):
        sshcp = Sshcp(host="badhost", port=self.port, user=self.user, password=password)
        with self.assertRaises(SshcpError) as ctx:
            sshcp.shell("cd {}; pwd".format(self.local_dir))
        self.assertTrue("Bad hostname" in str(ctx.exception))

    @parameterized.expand(_PARAMS)
    @timeout_decorator.timeout(5)
    def test_shell_error_bad_command(self, _, password):
        sshcp = Sshcp(host=self.host, port=self.port, user=self.user, password=password)
        with self.assertRaises(SshcpError) as ctx:
            sshcp.shell("./some_bad_command.sh".format(self.local_dir))
        self.assertTrue("./some_bad_command.sh" in str(ctx.exception))
