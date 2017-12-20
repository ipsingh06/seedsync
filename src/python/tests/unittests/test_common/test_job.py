# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import time


from common import Job


class DummyError(Exception):
    pass


class DummyFailingJob(Job):
    def setup(self):
        # noinspection PyAttributeOutsideInit
        self.cleanup_run = False

    def execute(self):
        raise DummyError()

    def cleanup(self):
        # noinspection PyAttributeOutsideInit
        self.cleanup_run = True


class TestJob(unittest.TestCase):
    def test_exception_propagates(self):
        context = MagicMock()
        # noinspection PyTypeChecker
        job = DummyFailingJob("DummyFailingJob", context)
        job.start()
        time.sleep(0.2)
        with self.assertRaises(DummyError):
            job.propagate_exception()
        job.terminate()
        job.join()

    def test_cleanup_executes_on_execute_error(self):
        context = MagicMock()
        # noinspection PyTypeChecker
        job = DummyFailingJob("DummyFailingJob", context)
        job.start()
        time.sleep(0.2)
        job.terminate()
        job.join()
        self.assertTrue(job.cleanup_run)
