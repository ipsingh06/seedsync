# Copyright 2017, Inderpreet Singh, All rights reserved.

import getpass
import logging
import os
import shutil
import sys
import tempfile
import unittest
from filecmp import dircmp

import timeout_decorator

from lftp import Lftp


class TestLftp(unittest.TestCase):
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        # Create a temp directory
        TestLftp.temp_dir = tempfile.mkdtemp(prefix="test_lftp_")

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        shutil.rmtree(TestLftp.temp_dir)

    def setUp(self):
        os.mkdir(os.path.join(TestLftp.temp_dir, "remote"))
        os.mkdir(os.path.join(TestLftp.temp_dir, "local"))

        # Create default lftp instance
        # Note: password-less ssh needs to be setup
        #       i.e. user's public key needs to be in authorized_keys
        #       cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        self.lftp = Lftp(address="localhost", user=getpass.getuser(), password="")
        self.lftp.set_base_remote_dir_path(os.path.join(TestLftp.temp_dir, "remote"))
        self.lftp.set_base_local_dir_path(os.path.join(TestLftp.temp_dir, "local"))
        logger = logging.getLogger("TestLftp")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.lftp.set_base_logger(logger)

        # White-box logging
        Lftp._LOG_COMMAND_OUTPUT = True

    def tearDown(self):
        self.lftp.exit()
        shutil.rmtree(os.path.join(TestLftp.temp_dir, "remote"))
        shutil.rmtree(os.path.join(TestLftp.temp_dir, "local"))

    # noinspection PyMethodMayBeStatic
    def my_mkdir(self, *args):
        os.mkdir(os.path.join(TestLftp.temp_dir, "remote", *args))

    # noinspection PyMethodMayBeStatic
    def my_touch(self, size: int, *args):
        path = os.path.join(TestLftp.temp_dir, "remote", *args)
        with open(path, 'wb') as f:
            f.write(bytearray(os.urandom(size)))

    def assert_local_equals_remote(self):
        dcmp = dircmp(os.path.join(TestLftp.temp_dir, "remote"),
                      os.path.join(TestLftp.temp_dir, "local"))
        self.assertFalse(dcmp.left_only)
        self.assertFalse(dcmp.right_only)
        self.assertFalse(dcmp.diff_files)

    @timeout_decorator.timeout(5)
    def test_download_1(self):
        """File names with single quotes"""
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 300

        self.my_mkdir("aaa'aaa")
        self.my_touch(128, "aaa'aaa", "aa'aa'aa.txt")
        self.my_touch(256, "b''b''b.txt")
        self.my_mkdir("c'c'c'c")
        self.my_touch(100, "c'c'c'c", "c'''c.txt")
        self.my_touch(200, "d'''d.txt")

        self.lftp.queue("aaa'aaa", True)
        self.lftp.queue("b''b''b.txt", False)
        self.lftp.queue("c'c'c'c", True)
        self.lftp.queue("d'''d.txt", False)

        # Wait until all downloads are done
        while self.lftp.status():
            pass

        self.assert_local_equals_remote()

    @timeout_decorator.timeout(5)
    def test_download_2(self):
        """File names with double quotes"""
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 300

        self.my_mkdir("aaa\"aaa")
        self.my_touch(128, "aaa\"aaa", "aa\"aa\"aa.txt")
        self.my_touch(256, "b\"\"b\"\"b.txt")
        self.my_mkdir("c\"c\"c\"c")
        self.my_touch(100, "c\"c\"c\"c", "c\"\"\"c.txt")
        self.my_touch(200, "d\"\"\"d.txt")

        self.lftp.queue("aaa\"aaa", True)
        self.lftp.queue("b\"\"b\"\"b.txt", False)
        self.lftp.queue("c\"c\"c\"c", True)
        self.lftp.queue("d\"\"\"d.txt", False)

        # Wait until all downloads are done
        while self.lftp.status():
            pass

        self.assert_local_equals_remote()

    @timeout_decorator.timeout(5)
    def test_download_3(self):
        """File names with quotes and spaces"""
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 300

        self.my_mkdir("a' aa\"aaa")
        self.my_touch(128, "a' aa\"aaa", "aa\"a ' a\"aa.txt")
        self.my_touch(256, "\"b ' \"b\" ' \"b.txt")
        self.my_mkdir("'c\" c \" 'c' \"c\"")
        self.my_touch(100, "'c\" c \" 'c' \"c\"", "c' \" ' \" ' \"c.txt")
        self.my_touch(200, "d\" ' \" ' \"d.txt")

        self.lftp.queue("a' aa\"aaa", True)
        self.lftp.queue("\"b ' \"b\" ' \"b.txt", False)
        self.lftp.queue("'c\" c \" 'c' \"c\"", True)
        self.lftp.queue("d\" ' \" ' \"d.txt", False)

        # Wait until all downloads are done
        while self.lftp.status():
            pass

        self.assert_local_equals_remote()

    @timeout_decorator.timeout(5)
    def test_download_4(self):
        """File names with ' -o '"""
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 300

        self.my_mkdir("a -o a")
        self.my_touch(128, "a -o a", "a -o a.txt")
        self.my_touch(256, "b -o b.txt")
        self.my_mkdir("c -o c")
        self.my_touch(100, "c -o c", "c -o c.txt")
        self.my_touch(200, "d -o d.txt")

        self.lftp.queue("a -o a", True)
        self.lftp.queue("b -o b.txt", False)
        self.lftp.queue("c -o c", True)
        self.lftp.queue("d -o d.txt", False)

        # Wait until all downloads are done
        while self.lftp.status():
            pass

        self.assert_local_equals_remote()
