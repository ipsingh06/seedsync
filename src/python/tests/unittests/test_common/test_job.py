# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import time


from common import PylftpJob


class DummyError(Exception):
    pass


class DummyFailingJob(PylftpJob):
    def setup(self):
        pass

    def execute(self):
        raise DummyError()

    def cleanup(self):
        pass


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
