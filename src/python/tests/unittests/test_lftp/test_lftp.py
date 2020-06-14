# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import os
import shutil
import sys
import tempfile
import unittest

import timeout_decorator

from tests.utils import TestUtils
from lftp import Lftp, LftpJobStatus, LftpError


# noinspection PyPep8Naming,SpellCheckingInspection
class TestLftp(unittest.TestCase):
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        # Create a temp directory
        TestLftp.temp_dir = tempfile.mkdtemp(prefix="test_lftp_")

        # Allow group access for the seedsynctest account
        TestUtils.chmod_from_to(TestLftp.temp_dir, tempfile.gettempdir(), 0o775)

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
        self.local_dir = os.path.join(TestLftp.temp_dir, "local")
        self.remote_dir = os.path.join(TestLftp.temp_dir, "remote")

        # Note: seedsynctest account must be set up. See DeveloperReadme.md for details
        self.host = "localhost"
        self.port = 22
        self.user = "seedsynctest"
        self.password = "seedsyncpass"

        # Default lftp instance - use key-based login
        self.lftp = Lftp(address=self.host, port=self.port, user=self.user, password=None)
        self.lftp.set_base_remote_dir_path(self.remote_dir)
        self.lftp.set_base_local_dir_path(self.local_dir)
        self.lftp.set_verbose_logging(True)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def tearDown(self):
        self.lftp.exit()

    def test_num_connections_per_dir_file(self):
        self.lftp.num_connections_per_dir_file = 5
        self.assertEqual(5, self.lftp.num_connections_per_dir_file)
        with self.assertRaises(ValueError):
            self.lftp.num_connections_per_dir_file = -1

    def test_num_connections_per_root_file(self):
        self.lftp.num_connections_per_root_file = 5
        self.assertEqual(5, self.lftp.num_connections_per_root_file)
        with self.assertRaises(ValueError):
            self.lftp.num_connections_per_root_file = -1

    def test_num_parallel_files(self):
        self.lftp.num_parallel_files = 5
        self.assertEqual(5, self.lftp.num_parallel_files)
        with self.assertRaises(ValueError):
            self.lftp.num_parallel_files = -1

    def test_num_max_total_connections(self):
        self.lftp.num_max_total_connections = 5
        self.assertEqual(5, self.lftp.num_max_total_connections)
        self.lftp.num_max_total_connections = 0
        self.assertEqual(0, self.lftp.num_max_total_connections)
        with self.assertRaises(ValueError):
            self.lftp.num_max_total_connections = -1

    def test_rate_limit(self):
        self.lftp.rate_limit = 500
        self.assertEqual("500", self.lftp.rate_limit)
        self.lftp.rate_limit = "2k"
        self.assertEqual("2k", self.lftp.rate_limit)
        self.lftp.rate_limit = "1M"
        self.assertEqual("1M", self.lftp.rate_limit)

    def test_min_chunk_size(self):
        self.lftp.min_chunk_size = 500
        self.assertEqual("500", self.lftp.min_chunk_size)
        self.lftp.min_chunk_size = "2k"
        self.assertEqual("2k", self.lftp.min_chunk_size)
        self.lftp.min_chunk_size = "1M"
        self.assertEqual("1M", self.lftp.min_chunk_size)

    def test_num_parallel_jobs(self):
        self.lftp.num_parallel_jobs = 5
        self.assertEqual(5, self.lftp.num_parallel_jobs)
        with self.assertRaises(ValueError):
            self.lftp.num_parallel_jobs = -1

    def test_move_background_on_exit(self):
        self.lftp.move_background_on_exit = True
        self.assertEqual(True, self.lftp.move_background_on_exit)
        self.lftp.move_background_on_exit = False
        self.assertEqual(False, self.lftp.move_background_on_exit)

    def test_use_temp_file(self):
        self.lftp.use_temp_file = True
        self.assertEqual(True, self.lftp.use_temp_file)
        self.lftp.use_temp_file = False
        self.assertEqual(False, self.lftp.use_temp_file)

    def test_temp_file_name(self):
        self.lftp.temp_file_name = "*.lftp"
        self.assertEqual("*.lftp", self.lftp.temp_file_name)
        self.lftp.temp_file_name = "*.temp"
        self.assertEqual("*.temp", self.lftp.temp_file_name)

    def test_sftp_auto_confirm(self):
        self.lftp.sftp_auto_confirm = True
        self.assertEqual(True, self.lftp.sftp_auto_confirm)
        self.lftp.sftp_auto_confirm = False
        self.assertEqual(False, self.lftp.sftp_auto_confirm)

    def test_sftp_connect_program(self):
        self.lftp.sftp_connect_program = "program -a -f"
        self.assertEqual("\"program -a -f\"", self.lftp.sftp_connect_program)
        self.lftp.sftp_connect_program = "\"abc -d\""
        self.assertEqual("\"abc -d\"", self.lftp.sftp_connect_program)

    def test_status_empty(self):
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queue_file(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("c", False)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("c", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_queue_dir(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_queue_file_with_spaces(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("d d", False)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("d d", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.PGET, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_queue_dir_with_spaces(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("e e", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("e e", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_queue_num_parallel_jobs(self):
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 2:
                break
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

    @timeout_decorator.timeout(20)
    def test_kill_all(self):
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 2:
                break
        self.assertEqual(3, len(statuses))
        self.lftp.kill_all()
        statuses = self.lftp.status()
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_kill_all_and_queue_again(self):
        self.lftp.num_parallel_jobs = 2
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        self.lftp.queue("c", False)
        self.lftp.queue("b", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 2:
                break
        self.assertEqual(3, len(statuses))
        self.lftp.kill_all()
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.assertEqual(0, len(statuses))
        self.lftp.queue("b", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("b", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_kill_queued_job(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.num_parallel_jobs = 1
        self.lftp.queue("a", True)  # this job will run
        self.lftp.queue("b", True)  # this job will queue
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 1:
                break
        self.assertEqual(2, len(statuses))
        self.assertEqual("b", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.QUEUED, statuses[0].state)
        self.assertEqual("a", statuses[1].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[1].state)
        self.assertEqual(True, self.lftp.kill("b"))
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

    @timeout_decorator.timeout(20)
    def test_kill_running_job(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)
        self.assertEqual(True, self.lftp.kill("a"))
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_kill_missing_job(self):
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)
        self.assertEqual(False, self.lftp.kill("b"))
        self.assertEqual(True, self.lftp.kill("a"))
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_kill_job_1(self):
        """Queued and running jobs killed one at a time"""
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.num_parallel_jobs = 2
        # 2 jobs running, 3 jobs queued
        self.lftp.queue("a", True)  # running
        self.lftp.queue("d d", False)  # running
        self.lftp.queue("b", True)  # queued
        self.lftp.queue("c", False)  # queued
        self.lftp.queue("e e", True)  # queued

        Q = LftpJobStatus.State.QUEUED
        R = LftpJobStatus.State.RUNNING

        while True:
            statuses = self.lftp.status()
            if len(statuses) > 4:
                break
        self.assertEqual(5, len(statuses))
        self.assertEqual(["b", "c", "e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, Q, Q, R, R], [s.state for s in statuses])

        # kill the queued jobs one-by-one
        self.lftp.kill("c")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 4:
                break
        self.assertEqual(4, len(statuses))
        self.assertEqual(["b", "e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, Q, R, R], [s.state for s in statuses])
        self.lftp.kill("b")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 3:
                break
        self.assertEqual(3, len(statuses))
        self.assertEqual(["e e", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])
        self.lftp.kill("e e")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 2:
                break
        self.assertEqual(2, len(statuses))
        self.assertEqual(["a", "d d"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])
        # kill the running jobs one-by-one
        self.lftp.kill("d d")
        statuses = self.lftp.status()
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 1:
                break
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(R, statuses[0].state)
        self.lftp.kill("a")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queued_and_kill_jobs_1(self):
        """Queued and running jobs killed one at a time"""
        self.lftp.rate_limit = 10  # so jobs don't finish right away
        self.lftp.num_parallel_jobs = 2

        Q = LftpJobStatus.State.QUEUED
        R = LftpJobStatus.State.RUNNING

        # add 3 jobs - a, dd, b
        self.lftp.queue("a", True)
        self.lftp.queue("d d", False)
        self.lftp.queue("b", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 2:
                break
        self.assertEqual(3, len(statuses))
        self.assertEqual(["b", "a", "d d"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])

        # remove dd (running)
        self.lftp.kill("d d")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 2:
                break
        self.assertEqual(2, len(statuses))
        self.assertEqual(["a", "b"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])

        # remove a (running)
        self.lftp.kill("a")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 1:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual(["b"], [s.name for s in statuses])
        self.assertEqual([R], [s.state for s in statuses])

        # add 3 jobs - c, ee, a
        self.lftp.queue("c", False)
        self.lftp.queue("e e", True)
        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 4:
                break
        self.assertEqual(4, len(statuses))
        self.assertEqual(["e e", "a", "b", "c"], [s.name for s in statuses])
        self.assertEqual([Q, Q, R, R], [s.state for s in statuses])

        # remove ee (queued) and b (running)
        self.lftp.kill("e e")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 3:
                break
        self.assertEqual(3, len(statuses))
        self.assertEqual(["a", "b", "c"], [s.name for s in statuses])
        self.assertEqual([Q, R, R], [s.state for s in statuses])
        self.lftp.kill("b")
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 2:
                break
        self.assertEqual(2, len(statuses))
        self.assertEqual(["c", "a"], [s.name for s in statuses])
        self.assertEqual([R, R], [s.state for s in statuses])

        # remove all
        self.lftp.kill_all()
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queue_dir_wrong_file_type(self):
        """check that queueing a dir with PGET fails gracefully"""
        # passing dir as a file
        print("Queuing dir as a file")
        self.lftp.queue("a", False)
        # wait for command to fail
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        with self.assertRaises(LftpError) as ctx:
            self.lftp.raise_pending_error()
        self.assertTrue("Access failed" in str(ctx.exception))
        # next status should be empty
        print("Getting empty status")
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queue_file_wrong_file_type(self):
        """check that queueing a file with MIRROR fails gracefully"""
        # passing file as a dir
        print("Queuing file as a dir")
        self.lftp.queue("c", True)
        # wait for command to fail
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        with self.assertRaises(LftpError) as ctx:
            self.lftp.raise_pending_error()
        self.assertTrue("Access failed" in str(ctx.exception))
        # next status should be empty
        print("Getting empty status")
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queue_missing_file(self):
        """check that queueing non-existing file fails gracefully"""
        self.lftp.queue("non-existing-file", False)
        # wait for command to fail
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        with self.assertRaises(LftpError) as ctx:
            self.lftp.raise_pending_error()
        self.assertTrue("No such file" in str(ctx.exception))
        # next status should be empty
        print("Getting empty status")
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_queue_missing_dir(self):
        """check that queueing non-existing directory fails gracefully"""

        self.lftp.queue("non-existing-folder", True)
        # wait for command to fail
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        with self.assertRaises(LftpError) as ctx:
            self.lftp.raise_pending_error()
        self.assertTrue("No such file" in str(ctx.exception))
        # next status should be empty
        print("Getting empty status")
        statuses = self.lftp.status()
        self.assertEqual(0, len(statuses))

    @timeout_decorator.timeout(20)
    def test_password_auth(self):
        # exit the default instance
        self.lftp.exit()

        self.lftp = Lftp(address=self.host, port=self.port, user=self.user, password=self.password)
        self.lftp.set_base_remote_dir_path(self.remote_dir)
        self.lftp.set_base_local_dir_path(self.local_dir)
        self.lftp.set_verbose_logging(True)

        # Disable key-based auth
        program = self.lftp.sftp_connect_program
        program = program[:-1]  # remove the end double-quote
        program += " -oPubkeyAuthentication=no\""
        self.lftp.sftp_connect_program = program

        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

        # Wait for empty status
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        self.lftp.raise_pending_error()

    @timeout_decorator.timeout(20)
    def test_error_bad_password(self):
        # exit the default instance
        self.lftp.exit()

        self.lftp = Lftp(address=self.host, port=self.port, user=self.user, password="wrong password")
        self.lftp.set_base_remote_dir_path(self.remote_dir)
        self.lftp.set_base_local_dir_path(self.local_dir)
        self.lftp.set_verbose_logging(True)
        self.lftp.rate_limit = 10  # so jobs don't finish right away

        # Disable key-based auth
        program = self.lftp.sftp_connect_program
        program = program[:-1]  # remove the end double-quote
        program += " -oPubkeyAuthentication=no\""
        self.lftp.sftp_connect_program = program

        self.lftp.queue("a", True)
        while True:
            statuses = self.lftp.status()
            if len(statuses) > 0:
                break
        self.assertEqual(1, len(statuses))
        self.assertEqual("a", statuses[0].name)
        self.assertEqual(LftpJobStatus.Type.MIRROR, statuses[0].type)
        self.assertEqual(LftpJobStatus.State.RUNNING, statuses[0].state)

        # Wait for empty status
        while True:
            statuses = self.lftp.status()
            if len(statuses) == 0:
                break
        with self.assertRaises(LftpError) as ctx:
            self.lftp.raise_pending_error()
        self.assertTrue("Login failed: Login incorrect" in str(ctx.exception))
