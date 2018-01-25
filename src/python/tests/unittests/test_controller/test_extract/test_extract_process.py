# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import logging
from unittest.mock import patch
import sys
import multiprocessing
import ctypes
import threading
import time

import timeout_decorator

from model import ModelFile
from controller.extract import ExtractProcess, ExtractListener, ExtractStatus


class TestExtractProcess(unittest.TestCase):
    def setUp(self):
        dispatch_patcher = patch('controller.extract.extract_process.ExtractDispatch')
        self.addCleanup(dispatch_patcher.stop)
        self.mock_dispatch_cls = dispatch_patcher.start()
        self.mock_dispatch = self.mock_dispatch_cls.return_value

        # by default mock returns empty statuses
        self.mock_dispatch.status.return_value = []

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

    @timeout_decorator.timeout(2)
    def test_param_out_dir_path(self):
        self.out_dir_path = multiprocessing.Manager().Value(ctypes.c_char_p, "")
        self.ctor_called = multiprocessing.Value('i', 0)

        def mock_ctor(**kwargs):
            self.out_dir_path.value = kwargs["out_dir_path"]
            self.ctor_called.value = 1
            return self.mock_dispatch
        self.mock_dispatch_cls.side_effect = mock_ctor

        self.process = ExtractProcess(out_dir_path="/test/out/path",
                                      local_path="/test/local/path")
        self.process.start()
        # Wait for ctor to be called
        while self.ctor_called.value == 0:
            pass
        self.assertEqual("/test/out/path", self.out_dir_path.value)

    @timeout_decorator.timeout(2)
    def test_param_out_local_path(self):
        self.local_path = multiprocessing.Manager().Value(ctypes.c_char_p, "")
        self.ctor_called = multiprocessing.Value('i', 0)

        def mock_ctor(**kwargs):
            self.local_path.value = kwargs["local_path"]
            self.ctor_called.value = 1
            return self.mock_dispatch
        self.mock_dispatch_cls.side_effect = mock_ctor

        self.process = ExtractProcess(out_dir_path="/test/out/path",
                                      local_path="/test/local/path")
        self.process.start()
        # Wait for ctor to be called
        while self.ctor_called.value == 0:
            pass
        self.assertEqual("/test/local/path", self.local_path.value)

    @timeout_decorator.timeout(2)
    def test_calls_start_dispatch(self):
        self.start_called = multiprocessing.Value('i', 0)

        def _start():
            self.start_called.value = 1
        self.mock_dispatch.start.side_effect = _start

        self.process = ExtractProcess(out_dir_path="/test/out/path",
                                      local_path="/test/local/path")
        self.process.start()
        while self.start_called.value == 0:
            pass

    @timeout_decorator.timeout(10)
    def test_retrieves_status(self):
        # Use this as a signal to mock to control which status to send
        self.status_signal = multiprocessing.Value('i', 0)
        self.status_counter = multiprocessing.Value('i', 0)

        s_a = ExtractStatus(name="a", is_dir=True, state=ExtractStatus.State.EXTRACTING)
        s_b = ExtractStatus(name="b", is_dir=False, state=ExtractStatus.State.EXTRACTING)
        s_c = ExtractStatus(name="c", is_dir=True, state=ExtractStatus.State.EXTRACTING)

        def _status():
            ret = None
            if self.status_signal.value == 0:
                ret = [s_a]
            elif self.status_signal.value == 1:
                ret = [s_a, s_b]
            elif self.status_signal.value == 2:
                ret = [s_c]
            elif self.status_signal.value == 3:
                ret = []
            self.status_counter.value += 1
            return ret
        self.mock_dispatch.status.side_effect = _status

        self.process = ExtractProcess(out_dir_path="", local_path="")
        self.process.start()

        # wait for first call to status (actually second call to guarantee first status is queued)
        while self.status_counter.value < 2:
            pass
        status_result = self.process.pop_latest_statuses()
        self.assertEqual(1, len(status_result.statuses))
        self.assertEqual("a", status_result.statuses[0].name)
        self.assertEqual(True, status_result.statuses[0].is_dir)
        self.assertEqual(ExtractStatus.State.EXTRACTING, status_result.statuses[0].state)

        # signal for status #1 and wait status fetch
        self.status_signal.value = 1
        orig_counter = self.status_counter.value
        while self.status_counter.value < orig_counter+2:
            pass
        status_result = self.process.pop_latest_statuses()
        self.assertEqual(2, len(status_result.statuses))
        self.assertEqual("a", status_result.statuses[0].name)
        self.assertEqual(True, status_result.statuses[0].is_dir)
        self.assertEqual(ExtractStatus.State.EXTRACTING, status_result.statuses[0].state)
        self.assertEqual("b", status_result.statuses[1].name)
        self.assertEqual(False, status_result.statuses[1].is_dir)
        self.assertEqual(ExtractStatus.State.EXTRACTING, status_result.statuses[1].state)

        # signal for status #2 and wait status fetch
        self.status_signal.value = 2
        orig_counter = self.status_counter.value
        while self.status_counter.value < orig_counter+2:
            pass
        status_result = self.process.pop_latest_statuses()
        self.assertEqual(1, len(status_result.statuses))
        self.assertEqual("c", status_result.statuses[0].name)
        self.assertEqual(True, status_result.statuses[0].is_dir)
        self.assertEqual(ExtractStatus.State.EXTRACTING, status_result.statuses[0].state)

        # signal for status #3 and wait status fetch
        self.status_signal.value = 3
        orig_counter = self.status_counter.value
        while self.status_counter.value < orig_counter+2:
            pass
        status_result = self.process.pop_latest_statuses()
        self.assertEqual(0, len(status_result.statuses))

    @timeout_decorator.timeout(10)
    def test_retrieves_completed(self):
        # Use this as a signal to mock to control which completed list to send
        self.completed_signal = multiprocessing.Value('i', 0)
        self.completed_counter = multiprocessing.Value('i', 0)

        def _add_listener(listener: ExtractListener):
            print("Listener added")

            def _callback_sequence():
                listener.extract_completed(name="a", is_dir=True)
                time.sleep(0.1)
                self.completed_signal.value = 1

                time.sleep(1.0)
                listener.extract_completed(name="b", is_dir=False)
                listener.extract_completed(name="c", is_dir=True)
                time.sleep(0.1)
                self.completed_signal.value = 2

            threading.Thread(target=_callback_sequence()).start()
        self.mock_dispatch.add_listener.side_effect = _add_listener

        self.process = ExtractProcess(out_dir_path="", local_path="")
        self.process.start()

        while self.completed_signal.value < 1:
            pass
        completed = self.process.pop_completed()
        self.assertEqual(1, len(completed))
        self.assertEqual("a", completed[0].name)
        self.assertEqual(True, completed[0].is_dir)
        # next one should be empty
        completed = self.process.pop_completed()
        self.assertEqual(0, len(completed))

        while self.completed_signal.value < 2:
            pass
        completed = self.process.pop_completed()
        self.assertEqual(2, len(completed))
        self.assertEqual("b", completed[0].name)
        self.assertEqual(False, completed[0].is_dir)
        self.assertEqual("c", completed[1].name)
        self.assertEqual(True, completed[1].is_dir)
        # next one should be empty
        completed = self.process.pop_completed()
        self.assertEqual(0, len(completed))

    @timeout_decorator.timeout(5)
    def test_forwards_extract_commands(self):
        a = ModelFile("a", True)
        a.local_size = 100
        aa = ModelFile("aa", False)
        aa.local_size = 60
        a.add_child(aa)
        ab = ModelFile("ab", False)
        ab.local_size = 40
        a.add_child(ab)

        b = ModelFile("b", True)
        b.local_size = 10
        ba = ModelFile("ba", True)
        ba.local_size = 10
        b.add_child(ba)
        baa = ModelFile("baa", False)
        baa.local_size = 10
        ba.add_child(baa)

        c = ModelFile("c", False)
        c.local_size = 1234

        self.extract_counter = multiprocessing.Value('i', 0)

        def _extract(file: ModelFile):
            print(file.name)
            if self.extract_counter.value == 0:
                self.assertEqual("a", file.name)
                self.assertEqual(True, file.is_dir)
                self.assertEqual(100, file.local_size)
                children = file.get_children()
                self.assertEqual(2, len(children))
                self.assertEqual("aa", children[0].name)
                self.assertEqual(False, children[0].is_dir)
                self.assertEqual(60, children[0].local_size)
                self.assertEqual("ab", children[1].name)
                self.assertEqual(False, children[0].is_dir)
                self.assertEqual(40, children[1].local_size)
            elif self.extract_counter.value == 1:
                self.assertEqual("b", file.name)
                self.assertEqual(True, file.is_dir)
                self.assertEqual(10, file.local_size)
                self.assertEqual(1, len(file.get_children()))
                child = file.get_children()[0]
                self.assertEqual("ba", child.name)
                self.assertEqual(True, child.is_dir)
                self.assertEqual(10, child.local_size)
                self.assertEqual(1, len(child.get_children()))
                subchild = child.get_children()[0]
                self.assertEqual("baa", subchild.name)
                self.assertEqual(False, subchild.is_dir)
                self.assertEqual(10, subchild.local_size)
            elif self.extract_counter.value == 2:
                self.assertEqual("c", file.name)
                self.assertEqual(False, file.is_dir)
                self.assertEqual(1234, file.local_size)
            self.extract_counter.value += 1
        self.mock_dispatch.extract.side_effect = _extract

        self.process = ExtractProcess(out_dir_path="", local_path="")
        self.process.start()

        self.process.extract(a)
        time.sleep(1)
        self.process.extract(b)
        self.process.extract(c)
        while self.extract_counter.value < 3:
            pass
