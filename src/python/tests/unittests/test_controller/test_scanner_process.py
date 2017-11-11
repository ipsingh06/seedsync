# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys
from multiprocessing import Queue
import time

import timeout_decorator

from controller import IScanner, ScannerProcess
from system import SystemFile


class DummyScanner(IScanner):
    def scan(self):
        return []

    def set_base_logger(self, base_logger: logging.Logger):
        pass


class DummyException(Exception):
    pass


class DummyFailingScanner(IScanner):
    def scan(self):
        raise DummyException("")

    def set_base_logger(self, base_logger: logging.Logger):
        pass


class TestScannerProcess(unittest.TestCase):
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
        queue = Queue()
        scanner = DummyFailingScanner()
        self.process = ScannerProcess(queue, scanner, 100)
        self.process.start()
        time.sleep(0.2)
        with self.assertRaises(DummyException):
            self.process.propagate_exception()

    @timeout_decorator.timeout(5)
    def test_process_terminates(self):
        queue = Queue()
        scanner = DummyScanner()
        self.process = ScannerProcess(queue, scanner, 1000)
        self.process.start()
        self.process.terminate()
        self.process = None

    @timeout_decorator.timeout(5)
    def test_scan_results(self):
        queue = Queue()
        scanner = DummyScanner()
        scanner.scan = MagicMock()
        scanner.scan.side_effect = [
            [SystemFile("first", 1, False)],
            [SystemFile("first", 1, False), SystemFile("second", 2, False)],
            [SystemFile("third", 3, True)],
        ]
        self.process = ScannerProcess(queue, scanner, 100)
        self.process.start()
        result = queue.get()
        self.assertEqual([SystemFile("first", 1, False)], result.files)
        result = queue.get()
        self.assertEqual([SystemFile("first", 1, False), SystemFile("second", 2, False)],
                         result.files)
        result = queue.get()
        self.assertEqual([SystemFile("third", 3, True)], result.files)
        self.process.terminate()

    @timeout_decorator.timeout(5)
    def test_scan_interval(self):
        """Check that result timestamp diffs are close to the specified interval (within 20%)"""
        queue = Queue()
        scanner = DummyScanner()

        self.process = ScannerProcess(queue, scanner, 100)
        self.process.start()
        result1 = queue.get()
        result2 = queue.get()
        delta_in_ms = int((result2.timestamp - result1.timestamp).total_seconds()*1000)
        self.assertTrue(80 <= delta_in_ms <= 120)
        self.process.terminate()

        self.process = ScannerProcess(queue, scanner, 500)
        self.process.start()
        result1 = queue.get()
        result2 = queue.get()
        delta_in_ms = int((result2.timestamp - result1.timestamp).total_seconds()*1000)
        self.assertTrue(400 <= delta_in_ms <= 600)
        self.process.terminate()
