# Copyright 2017, Inderpreet Singh, All rights reserved.

import getpass
import logging
import os
import shutil
import sys
import tempfile
import unittest
import time

from lftp import Lftp, LftpJobStatus, LftpError


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

    def test_status_empty(self):
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_queue_file(self):
        self.lftp.queue("c", False)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("c", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_queue_dir(self):
        self.lftp.queue("a", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_queue_file_with_spaces(self):
        self.lftp.queue("d d", False)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("d d", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_queue_dir_with_spaces(self):
        self.lftp.queue("e e", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("e e", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_queue_num_parallel_jobs(self):
        self.lftp.set_num_parallel_jobs(2)
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        # queued jobs
        self.assertEqual("b", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.QUEUED, statuses[0].state)
        # running jobs
        self.assertEqual("a", statuses[1].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[1].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[1].state)
        self.assertEqual("c", statuses[2].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[2].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[2].state)

    def test_kill_all(self):
        self.lftp.set_num_parallel_jobs(2)
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        self.lftp.kill_all()
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_kill_all_and_queue_again(self):
        self.lftp.set_num_parallel_jobs(2)
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        self.lftp.kill_all()
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))
        self.lftp.queue("b", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("b", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_kill_queued_job(self):
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.set_num_parallel_jobs(1)
        self.lftp.queue("a", True)  # this job will run
        self.lftp.queue("b", True)  # this job will queue
        statuses = self.lftp.status()
        self.assertEqual(2, len(statuses))
        self.assertEqual("b", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.QUEUED, statuses[0].state)
        self.assertEqual("a", statuses[1].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[1].state)
        self.assertEqual(True, self.lftp.kill("b"))
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    def test_kill_running_job(self):
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.queue("a", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)
        self.assertEqual(True, self.lftp.kill("a"))
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_kill_missing_job(self):
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.queue("a", True)
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)
        self.assertEqual(False, self.lftp.kill("b"))
        self.assertEqual(True, self.lftp.kill("a"))
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_kill_job_1(self):
        """Queued and running jobs killed one at a time"""
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.set_num_parallel_jobs(2)
        # 2 jobs running, 3 jobs queued
        self.lftp.queue("a", True)  # running
        self.lftp.queue("d d", False)  # running
        self.lftp.queue("b", True)  # queued
        self.lftp.queue("c", False)  # queued
        self.lftp.queue("e e", True)  # queued

        Q = LftpJobStatus.State.QUEUED
        R = LftpJobStatus.State.RUNNING

        statuses = self.lftp.status()
        self.assertEqual(5, len(statuses))
        self.assertEqual(["b", "c", "e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, Q, Q, R, R], [s.state for s in statuses])

        # kill the queued jobs one-by-one
        self.lftp.kill("c")
        statuses = self.lftp.status()
        self.assertEqual(4, len(statuses))
        self.assertEqual(["b", "e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, Q, R, R], [s.state for s in statuses])
        self.lftp.kill("b")
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        self.assertEqual(["e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])
        self.lftp.kill("e e")
        statuses = self.lftp.status()
        self.assertEqual(2, len(statuses))
        self.assertEqual(["a", "d d"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])
        # kill the running jobs one-by-one
        self.lftp.kill("d d")
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(R, statuses[0].state)
        self.lftp.kill("a")
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_queued_and_kill_jobs_1(self):
        """Queued and running jobs killed one at a time"""
        self.lftp.set_rate_limit(10)  # so jobs don't finish right away
        self.lftp.set_num_parallel_jobs(2)

        Q = LftpJobStatus.State.QUEUED
        R = LftpJobStatus.State.RUNNING

        # add 3 jobs - a, dd, b
        self.lftp.queue("a", True)
        self.lftp.queue("d d", False)
        self.lftp.queue("b", True)
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        self.assertEqual(["b", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])

        # remove dd (running)
        self.lftp.kill("d d")
        statuses = self.lftp.status()
        self.assertEqual(2, len(statuses))
        self.assertEqual(["a", "b"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])

        # remove a (running)
        self.lftp.kill("a")
        statuses = self.lftp.status()
        self.assertEqual(1, len(statuses))
        self.assertEqual(["b"], [s.name for s in statuses])
        self.assertEqual([R], [s.state for s in statuses])

        # add 3 jobs - c, ee, a
        self.lftp.queue("c", False)
        self.lftp.queue("e e", True)
        self.lftp.queue("a", True)
        statuses = self.lftp.status()
        self.assertEqual(4, len(statuses))
        self.assertEqual(["e e", "a", "b", "c"], [s.name for s in statuses])
        self.assertEqual([Q, Q, R, R], [s.state for s in statuses])

        # remove ee (queued) and b (running)
        self.lftp.kill("e e")
        statuses = self.lftp.status()
        self.assertEqual(3, len(statuses))
        self.assertEqual(["a", "b", "c"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])
        self.lftp.kill("b")
        statuses = self.lftp.status()
        self.assertEqual(2, len(statuses))
        self.assertEqual(["c", "a"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])

        # remove all
        self.lftp.kill_all()
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_queue_wrong_file_type(self):
        # check that queueing a file with MIRROR and a dir with PGET fails with an error

        # passing dir as a file
        self.lftp.queue("a", False)
        time.sleep(0.5)  # wait for jobs to connect
        # first status should raise an error
        with self.assertRaises(LftpError) as context:
            statuses = self.lftp.status()
        self.assertTrue(str(context.exception).startswith("Detected error:"))
        # second status should be empty
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

        # passing file as a dir
        self.lftp.queue("c", True)
        time.sleep(0.5)  # wait for jobs to connect
        # first status should raise an error
        with self.assertRaises(LftpError) as context:
            statuses = self.lftp.status()
        self.assertTrue(str(context.exception).startswith("Detected error:"))
        # second status should be empty
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    def test_queue_missing_file(self):
        # check that queueing non-existing file fails gracefully
        self.lftp.queue("non-existing-file", False)
        time.sleep(0.5)  # wait for jobs to connect
        with self.assertRaises(LftpError) as context:
            statuses = self.lftp.status()
        self.assertTrue(str(context.exception).startswith("Detected error:"))
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

        self.lftp.queue("non-existing-folder", True)
        time.sleep(0.5)  # wait for jobs to connect
        with self.assertRaises(LftpError) as context:
            statuses = self.lftp.status()
        self.assertTrue(str(context.exception).startswith("Detected error:"))
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))
