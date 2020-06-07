# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import multiprocessing
import logging
import sys
from unittest.mock import MagicMock

import timeout_decorator

from controller import IScanner, ScannerProcess, ScannerError
from system import SystemFile


class DummyScanner(IScanner):
    def scan(self):
        return []

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

    @timeout_decorator.timeout(10)
    def test_retrieves_scan_results(self):
        # Use this as a signal to mock to control which result to send
        self.scan_signal = multiprocessing.Value('i', 0)
        self.scan_counter = multiprocessing.Value('i', 0)

        a = SystemFile("a", 100, True)
        aa = SystemFile("aa", 60, False)
        a.add_child(aa)
        ab = SystemFile("ab", 40, False)
        a.add_child(ab)

        b = SystemFile("b", 10, True)
        ba = SystemFile("ba", 10, True)
        b.add_child(ba)
        baa = SystemFile("baa", 10, False)
        ba.add_child(baa)

        c = SystemFile("c", 1234, False)

        mock_scanner = DummyScanner()
        mock_scanner.scan = MagicMock()

        def _scan():
            ret = None
            if self.scan_signal.value == 0:
                ret = [a]
            elif self.scan_signal.value == 1:
                ret = [a, b]
            elif self.scan_signal.value == 2:
                ret = [c]
            elif self.scan_signal.value == 3:
                ret = []
            self.scan_counter.value += 1
            return ret
        mock_scanner.scan.side_effect = _scan

        self.process = ScannerProcess(scanner=mock_scanner,
                                      interval_in_ms=100)
        self.process.start()

        # wait for first call to scan (actually second call to guarantee first scan is queued)
        while self.scan_counter.value < 2:
            pass
        result = self.process.pop_latest_result()
        self.assertEqual(1, len(result.files))
        self.assertEqual("a", result.files[0].name)
        self.assertEqual(True, result.files[0].is_dir)
        self.assertEqual(100, result.files[0].size)
        self.assertEqual(2, len(result.files[0].children))
        self.assertEqual("aa", result.files[0].children[0].name)
        self.assertEqual(False, result.files[0].children[0].is_dir)
        self.assertEqual(60, result.files[0].children[0].size)
        self.assertEqual("ab", result.files[0].children[1].name)
        self.assertEqual(False, result.files[0].children[1].is_dir)
        self.assertEqual(40, result.files[0].children[1].size)

        # signal for scan #1 and wait scan fetch
        self.scan_signal.value = 1
        orig_counter = self.scan_counter.value
        while self.scan_counter.value < orig_counter+2:
            pass
        result = self.process.pop_latest_result()
        self.assertEqual(2, len(result.files))
        self.assertEqual("a", result.files[0].name)
        self.assertEqual(True, result.files[0].is_dir)
        self.assertEqual(100, result.files[0].size)
        self.assertEqual(2, len(result.files[0].children))
        self.assertEqual("aa", result.files[0].children[0].name)
        self.assertEqual(False, result.files[0].children[0].is_dir)
        self.assertEqual(60, result.files[0].children[0].size)
        self.assertEqual("ab", result.files[0].children[1].name)
        self.assertEqual(False, result.files[0].children[1].is_dir)
        self.assertEqual(40, result.files[0].children[1].size)
        self.assertEqual("b", result.files[1].name)
        self.assertEqual(True, result.files[1].is_dir)
        self.assertEqual(10, result.files[1].size)
        self.assertEqual(1, len(result.files[1].children))
        self.assertEqual("ba", result.files[1].children[0].name)
        self.assertEqual(True, result.files[1].children[0].is_dir)
        self.assertEqual(10, result.files[1].children[0].size)
        self.assertEqual(1, len(result.files[1].children[0].children))
        self.assertEqual("baa", result.files[1].children[0].children[0].name)
        self.assertEqual(False, result.files[1].children[0].children[0].is_dir)
        self.assertEqual(10, result.files[1].children[0].children[0].size)

        # signal for scan #2 and wait scan fetch
        self.scan_signal.value = 2
        orig_counter = self.scan_counter.value
        while self.scan_counter.value < orig_counter+2:
            pass
        result = self.process.pop_latest_result()
        self.assertEqual(1, len(result.files))
        self.assertEqual("c", result.files[0].name)
        self.assertEqual(False, result.files[0].is_dir)
        self.assertEqual(1234, result.files[0].size)

        # signal for scan #3 and wait scan fetch
        self.scan_signal.value = 3
        orig_counter = self.scan_counter.value
        while self.scan_counter.value < orig_counter+2:
            pass
        result = self.process.pop_latest_result()
        self.assertEqual(0, len(result.files))

    @timeout_decorator.timeout(10)
    def test_sends_error_result_on_recoverable_error(self):
        mock_scanner = DummyScanner()
        mock_scanner.scan = MagicMock()
        mock_scanner.scan.side_effect = ScannerError("recoverable error", recoverable=True)

        self.process = ScannerProcess(scanner=mock_scanner,
                                      interval_in_ms=100)
        self.process.start()

        while True:
            result = self.process.pop_latest_result()
            if result:
                break
        self.assertEqual(0, len(result.files))
        self.assertTrue(result.failed)
        self.assertEqual("recoverable error", result.error_message)

    @timeout_decorator.timeout(10)
    def test_sends_fatal_exception_on_nonrecoverable_error(self):
        mock_scanner = DummyScanner()
        mock_scanner.scan = MagicMock()
        mock_scanner.scan.side_effect = ScannerError("non-recoverable error", recoverable=False)

        self.process = ScannerProcess(scanner=mock_scanner,
                                      interval_in_ms=100)
        self.process.start()
        with self.assertRaises(ScannerError) as ctx:
            while True:
                self.process.propagate_exception()
        # noinspection PyUnreachableCode
        self.assertEqual("non-recoverable error", str(ctx.exception))
