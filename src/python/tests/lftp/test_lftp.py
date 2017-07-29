# Copyright 2017, Inderpreet Singh, All rights reserved.

import getpass
import logging
import os
import shutil
import sys
import tempfile
import unittest

from lftp import Lftp, LftpJobStatus


class TestLftp(unittest.TestCase):
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        # Create a temp directory
        TestLftp.temp_dir = tempfile.mkdtemp(prefix="test_lftp_")

        # Create some test directories
        # remote [dir] for remote path
        #   a [dir]
        #     aa [file,       24*1024 bytes]
        #     ab [file,  2*1024*1024 bytes]
        #   b [dir]
        #     ba [dir]
        #       baa [file, 128*1024 bytes]
        #       bab [file, 128*1024 bytes]
        #     bb [file, 128*1024 bytes]
        #   c [file, 1234 bytes]
        #   "d d" [file, 128*1024 bytes]
        #   "e e" [dir]
        #     "e e a" [file, 128*1024 bytes]
        # local [dir] for local path, cleared before every test

        def my_mkdir(*args):
            os.mkdir(os.path.join(TestLftp.temp_dir, *args))

        def my_touch(size, *args):
            path = os.path.join(TestLftp.temp_dir, *args)
            with open(path, 'wb') as f:
                f.write(bytearray([0xff]*size))

        my_mkdir("remote")
        my_mkdir("remote", "a")
        my_touch(24*1024, "remote", "a", "aa")
        my_touch(24*1024*1024, "remote", "a", "ab")
        my_mkdir("remote", "b")
        my_mkdir("remote", "b", "ba")
        my_touch(128*1024, "remote", "b", "ba", "baa")
        my_touch(128*1024, "remote", "b", "ba", "bab")
        my_touch(128*1024, "remote", "b", "bb")
        my_touch(1234, "remote", "c")
        my_touch(128*1024, "remote", "d d")
        my_mkdir("remote", "e e")
        my_touch(128*1024, "remote", "e e", "e e a")
        my_mkdir("local")

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        shutil.rmtree(TestLftp.temp_dir)

    def setUp(self):
        # Delete and recreate the local dir
        shutil.rmtree(os.path.join(TestLftp.temp_dir, "local"))
        os.mkdir(os.path.join(TestLftp.temp_dir, "local"))

        # Create default lftp instance
        # Note: password-less ssh needs to be setup
        #       i.e. user's public key needs to be in authorized_keys
        #       cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        self.lftp = Lftp(address="localhost", user=getpass.getuser(), password="")
        self.lftp.set_base_remote_dir_path(os.path.join(TestLftp.temp_dir, "remote"))
        self.lftp.set_base_local_dir_path(os.path.join(TestLftp.temp_dir, "local"))
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def test_set_num_connections(self):
        #TODO: change setters to properties
        self.lftp.set_num_connections(5)
        self.assertEqual(5, self.lftp.get_num_connections())
        with self.assertRaises(ValueError):
            self.lftp.set_num_connections(-1)

    def test_set_num_parallel_files(self):
        self.lftp.set_num_parallel_files(5)
        self.assertEqual(5, self.lftp.get_num_parallel_files())
        with self.assertRaises(ValueError):
            self.lftp.set_num_parallel_files(-1)

    def test_set_rate_limit(self):
        self.lftp.set_rate_limit(500)
        self.assertEqual("500", self.lftp.get_rate_limit())
        self.lftp.set_rate_limit("2k")
        self.assertEqual("2k", self.lftp.get_rate_limit())
        self.lftp.set_rate_limit("1M")
        self.assertEqual("1M", self.lftp.get_rate_limit())

    def test_set_min_chunk_size(self):
        self.lftp.set_min_chunk_size(500)
        self.assertEqual("500", self.lftp.get_min_chunk_size())
        self.lftp.set_min_chunk_size("2k")
        self.assertEqual("2k", self.lftp.get_min_chunk_size())
        self.lftp.set_min_chunk_size("1M")
        self.assertEqual("1M", self.lftp.get_min_chunk_size())

    def test_set_num_parallel_jobs(self):
        self.lftp.set_num_parallel_jobs(5)
        self.assertEqual(5, self.lftp.get_num_parallel_jobs())
        with self.assertRaises(ValueError):
            self.lftp.set_num_parallel_jobs(-1)

    def test_set_move_background_on_exit(self):
        self.lftp.set_move_background_on_exit(True)
        self.assertEqual(True, self.lftp.get_move_background_on_exit())
        self.lftp.set_move_background_on_exit(False)
        self.assertEqual(False, self.lftp.get_move_background_on_exit())

    def test_queue_file(self):
        self.lftp.queue("c", False)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("c", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_queue_dir(self):
        self.lftp.set_move_background_on_exit(False)
        self.lftp.set_rate_limit(100)
        self.lftp.queue("a", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)
