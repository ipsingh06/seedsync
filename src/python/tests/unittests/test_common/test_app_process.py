# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import logging
import sys
import time

import timeout_decorator

from common import AppProcess


class DummyException(Exception):
    pass


class DummyProcess(AppProcess):
    def __init__(self, fail: bool):
        super().__init__(name="DummyProcess")
        self.fail = fail

    def run_loop(self):
        if self.fail:
            raise DummyException()

    def run_init(self):
        pass


class TestAppProcess(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)

        # Assign process to this variable so that it can be cleaned up
        # even after an error
        self.process = None

    def tearDown(self):
        if self.process:
            self.process.terminate()

    def test_exception_propagates(self):
        self.process = DummyProcess(fail=True)
        self.process.start()
        time.sleep(0.2)
        with self.assertRaises(DummyException):
            self.process.propagate_exception()

    @timeout_decorator.timeout(5)
    def test_process_terminates(self):
        self.process = DummyProcess(fail=False)
        self.process.start()
        self.process.terminate()
        self.process = None
