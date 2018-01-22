# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
from unittest.mock import patch, MagicMock, call
import time

import timeout_decorator

from common import overrides
from model import ModelFile
from extract import ExtractDispatch, ExtractDispatchError, ExtractListener, \
                    ExtractError


class DummyExtractListener(ExtractListener):
    @overrides(ExtractListener)
    def extract_completed(self, name: str):
        pass

    @overrides(ExtractListener)
    def extract_failed(self, name: str):
        pass


class TestExtractDispatch(unittest.TestCase):
    def setUp(self):
        extract_patcher = patch('extract.dispatch.Extract')
        self.addCleanup(extract_patcher.stop)
        mock_extract_module = extract_patcher.start()
        self.mock_is_archive = mock_extract_module.is_archive
        self.mock_extract_archive = mock_extract_module.extract_archive

        self.out_dir_path = os.path.join("out", "dir")
        self.local_path = os.path.join("local", "path")
        self.dispatch = ExtractDispatch(
            out_dir_path=self.out_dir_path,
            local_path=self.local_path
        )

        self.listener = DummyExtractListener()
        self.listener.extract_completed = MagicMock()
        self.listener.extract_failed = MagicMock()

        self.dispatch.start()

    def tearDown(self):
        if self.dispatch:
            self.dispatch.stop()

    def test_extract_single_raises_error_on_remote_only_file(self):
        mf = ModelFile("aaa", False)
        mf.local_size = None
        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(mf)
        self.assertTrue(str(ctx.exception).startswith("File does not exist locally"))

        mf = ModelFile("aaa", False)
        mf.local_size = 0
        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(mf)
        self.assertTrue(str(ctx.exception).startswith("File does not exist locally"))

    def test_extract_single_raises_error_on_bad_archive(self):
        self.mock_is_archive.return_value = False

        mf = ModelFile("aaa", False)
        mf.local_size = 100

        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(mf)
        self.assertTrue(str(ctx.exception).startswith("File is not an archive"))
        self.mock_is_archive.assert_called_once_with(os.path.join(self.local_path, mf.name))

    @timeout_decorator.timeout(2)
    def test_extract_single(self):
        self.mock_is_archive.return_value = True

        mf = ModelFile("aaa", False)
        mf.local_size = 100

        self.dispatch.extract(mf)

        while self.mock_extract_archive.call_count < 1:
            pass
        self.mock_extract_archive.assert_called_once_with(
            archive_path=os.path.join(self.local_path, "aaa"),
            out_dir_path=self.out_dir_path
        )

    @timeout_decorator.timeout(2)
    def test_extract_maintains_order(self):
        self.mock_is_archive.return_value = True

        mf1 = ModelFile("aaa", False)
        mf1.local_size = 100
        mf2 = ModelFile("bbb", False)
        mf2.local_size = 100
        mf3 = ModelFile("ccc", False)
        mf3.local_size = 100

        self.dispatch.extract(mf1)
        self.dispatch.extract(mf2)
        self.dispatch.extract(mf3)

        while self.mock_extract_archive.call_count < 3:
            pass
        self.assertEqual(3, self.mock_extract_archive.call_count)
        args_list = self.mock_extract_archive.call_args_list
        self.assertEqual(args_list, [
            call(
                archive_path=os.path.join(self.local_path, "aaa"),
                out_dir_path=self.out_dir_path
            ),
            call(
                archive_path=os.path.join(self.local_path, "bbb"),
                out_dir_path=self.out_dir_path
            ),
            call(
                archive_path=os.path.join(self.local_path, "ccc"),
                out_dir_path=self.out_dir_path
            )
        ])

    @timeout_decorator.timeout(2)
    def test_extract_calls_listener_on_completed(self):
        self.mock_is_archive.return_value = True

        mf1 = ModelFile("aaa", False)
        mf1.local_size = 100

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(mf1)

        while self.mock_extract_archive.call_count < 1 \
                or self.listener.extract_completed.call_count < 1:
            pass
        self.assertEqual(1, self.mock_extract_archive.call_count)
        self.listener.extract_completed.assert_called_once_with("aaa")
        self.listener.extract_failed.assert_not_called()

    @timeout_decorator.timeout(2)
    def test_extract_calls_listener_on_failed(self):
        self.mock_is_archive.return_value = True

        # noinspection PyUnusedLocal
        def _extract_archive(**kwargs):
            raise ExtractError()
        self.mock_extract_archive.side_effect = _extract_archive

        mf1 = ModelFile("aaa", False)
        mf1.local_size = 100

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(mf1)

        while self.mock_extract_archive.call_count < 1 \
                or self.listener.extract_failed.call_count < 1:
            pass
        self.assertEqual(1, self.mock_extract_archive.call_count)
        self.listener.extract_completed.assert_not_called()
        self.listener.extract_failed.assert_called_once_with("aaa")

    @timeout_decorator.timeout(2)
    def test_extract_calls_listeners_in_correct_sequence(self):
        self.mock_is_archive.return_value = True
        self.count = 0

        # noinspection PyUnusedLocal
        def _extract_archive(**kwargs):
            # raise error for first and third extractions
            self.count += 1
            if self.count in (1, 3):
                raise ExtractError()
        self.mock_extract_archive.side_effect = _extract_archive

        mf1 = ModelFile("aaa", False)
        mf1.local_size = 100
        mf2 = ModelFile("bbb", False)
        mf2.local_size = 100
        mf3 = ModelFile("ccc", False)
        mf3.local_size = 100

        listener_calls = []

        def _completed(name):
            listener_calls.append((True, name))

        def _failed(name):
            listener_calls.append((False, name))

        self.listener.extract_completed.side_effect = _completed
        self.listener.extract_failed.side_effect = _failed

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(mf1)
        self.dispatch.extract(mf2)
        self.dispatch.extract(mf3)

        while self.mock_extract_archive.call_count < 3 \
                or self.listener.extract_failed.call_count < 2 \
                or self.listener.extract_completed.call_count < 1:
            pass
        self.assertEqual(3, self.mock_extract_archive.call_count)
        self.assertEqual([(False, "aaa"), (True, "bbb"), (False, "ccc")], listener_calls)

    @timeout_decorator.timeout(2)
    def test_extract_skips_remaining_on_shutdown(self):
        # Send two extract commands
        # Call shutdown after first one runs
        # Check that second command did not run
        self.mock_is_archive.return_value = True

        self.call_stop = False

        def _extract_archive(**kwargs):
            print(kwargs)
            self.call_stop = True
            time.sleep(0.5)  # wait a bit so shutdown is called

        self.mock_extract_archive.side_effect = _extract_archive

        mf1 = ModelFile("aaa", False)
        mf1.local_size = 100
        mf2 = ModelFile("bbb", False)
        mf2.local_size = 100

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(mf1)
        self.dispatch.extract(mf2)

        while not self.call_stop:
            pass
        self.dispatch.stop()

        while self.mock_extract_archive.call_count < 1 \
                or self.listener.extract_completed.call_count < 1:
            pass
        self.assertEqual(1, self.mock_extract_archive.call_count)
        self.listener.extract_completed.assert_called_once_with("aaa")
        self.listener.extract_failed.assert_called_once_with("bbb")

    def test_extract_dir_raises_error_on_empty_dir(self):
        mf = ModelFile("aaa", True)

        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(mf)
        self.assertTrue(str(ctx.exception).startswith("Directory does not contain any archives"))

    def test_extract_dir_raises_error_on_no_archives(self):
        self.mock_is_archive.return_value = False

        a = ModelFile("a", True)
        a.local_size = 100
        aa = ModelFile("aa", False)
        aa.local_size = 50
        a.add_child(aa)
        ab = ModelFile("ab", False)
        ab.local_size = 50
        a.add_child(ab)

        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(a)
        self.assertTrue(str(ctx.exception).startswith("Directory does not contain any archives"))

    def test_extract_dir_raises_error_on_no_local_files(self):
        self.mock_is_archive.return_value = True

        a = ModelFile("a", True)
        a.remote_size = 100
        aa = ModelFile("aa", False)
        aa.remote_size = 50
        a.add_child(aa)
        ab = ModelFile("ab", False)
        ab.remote_size = 50
        a.add_child(ab)

        with self.assertRaises(ExtractDispatchError) as ctx:
            self.dispatch.extract(a)
        self.assertTrue(str(ctx.exception).startswith("Directory does not contain any archives"))

    # noinspection SpellCheckingInspection
    @timeout_decorator.timeout(2)
    def test_extract_dir(self):
        self.mock_is_archive.return_value = True
        self.actual_calls = set()

        def _extract(archive_path: str, out_dir_path: str):
            self.actual_calls.add((archive_path, out_dir_path))
        self.mock_extract_archive.side_effect = _extract

        a = ModelFile("a", True)
        a.local_size = 500
        aa = ModelFile("aa", True)
        aa.local_size = 300
        a.add_child(aa)
        aaa = ModelFile("aaa", False)
        aaa.local_size = 100
        aa.add_child(aaa)
        aab = ModelFile("aab", False)
        aab.local_size = 100
        aa.add_child(aab)
        aac = ModelFile("aac", True)
        aac.local_size = 100
        aa.add_child(aac)
        aaca = ModelFile("aaca", False)
        aaca.local_size = 100
        aac.add_child(aaca)
        ab = ModelFile("ab", True)
        ab.local_size = 100
        a.add_child(ab)
        aba = ModelFile("aba", False)
        aba.local_size = 100
        ab.add_child(aba)
        ac = ModelFile("ac", False)
        ac.local_size = 100
        a.add_child(ac)

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(a)
        while self.listener.extract_completed.call_count < 1:
            pass
        self.listener.extract_completed.assert_called_once_with("a")

        golden_calls = {
            (
                os.path.join(self.local_path, "a", "aa", "aaa"),
                os.path.join(self.out_dir_path, "a", "aa")
            ),
            (
                os.path.join(self.local_path, "a", "aa", "aab"),
                os.path.join(self.out_dir_path, "a", "aa")
            ),
            (
                os.path.join(self.local_path, "a", "aa", "aac", "aaca"),
                os.path.join(self.out_dir_path, "a", "aa", "aac")
            ),
            (
                os.path.join(self.local_path, "a", "ab", "aba"),
                os.path.join(self.out_dir_path, "a", "ab")
            ),
            (
                os.path.join(self.local_path, "a", "ac"),
                os.path.join(self.out_dir_path, "a")
            ),
        }
        self.assertEqual(5, self.mock_extract_archive.call_count)
        self.assertEqual(golden_calls, self.actual_calls)

    # noinspection SpellCheckingInspection
    @timeout_decorator.timeout(2)
    def test_extract_dir_skips_remote_files(self):
        self.mock_is_archive.return_value = True
        self.actual_calls = set()

        def _extract(archive_path: str, out_dir_path: str):
            self.actual_calls.add((archive_path, out_dir_path))
        self.mock_extract_archive.side_effect = _extract

        a = ModelFile("a", True)
        a.local_size = 500
        aa = ModelFile("aa", True)
        aa.local_size = 300
        a.add_child(aa)
        aaa = ModelFile("aaa", False)
        aaa.local_size = 100
        aa.add_child(aaa)
        aab = ModelFile("aab", False)
        aab.remote_size = 100
        aa.add_child(aab)
        aac = ModelFile("aac", True)
        aac.local_size = 100
        aa.add_child(aac)
        aaca = ModelFile("aaca", False)
        aaca.local_size = 100
        aac.add_child(aaca)
        ab = ModelFile("ab", True)
        ab.local_size = 100
        a.add_child(ab)
        aba = ModelFile("aba", False)
        aba.local_size = 100
        ab.add_child(aba)
        ac = ModelFile("ac", False)
        ac.remote_size = 100
        a.add_child(ac)

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(a)
        while self.listener.extract_completed.call_count < 1:
            pass
        self.listener.extract_completed.assert_called_once_with("a")

        golden_calls = {
            (
                os.path.join(self.local_path, "a", "aa", "aaa"),
                os.path.join(self.out_dir_path, "a", "aa")
            ),
            (
                os.path.join(self.local_path, "a", "aa", "aac", "aaca"),
                os.path.join(self.out_dir_path, "a", "aa", "aac")
            ),
            (
                os.path.join(self.local_path, "a", "ab", "aba"),
                os.path.join(self.out_dir_path, "a", "ab")
            ),
        }
        self.assertEqual(3, self.mock_extract_archive.call_count)
        self.assertEqual(golden_calls, self.actual_calls)

    # noinspection SpellCheckingInspection
    @timeout_decorator.timeout(2)
    def test_extract_dir_skips_non_archive_files(self):
        # noinspection SpellCheckingInspection
        def _is_archive(archive_path: str):
            return archive_path in (
                os.path.join(self.local_path, "a", "aa", "aaa"),
                os.path.join(self.local_path, "a", "aa", "aac", "aaca"),
                os.path.join(self.local_path, "a", "ab", "aba")
            )
        self.mock_is_archive.side_effect = _is_archive
        self.actual_calls = set()

        def _extract(archive_path: str, out_dir_path: str):
            self.actual_calls.add((archive_path, out_dir_path))
        self.mock_extract_archive.side_effect = _extract

        a = ModelFile("a", True)
        a.local_size = 500
        aa = ModelFile("aa", True)
        aa.local_size = 300
        a.add_child(aa)
        aaa = ModelFile("aaa", False)
        aaa.local_size = 100
        aa.add_child(aaa)
        aab = ModelFile("aab", False)
        aab.local_size = 100
        aa.add_child(aab)
        aac = ModelFile("aac", True)
        aac.local_size = 100
        aa.add_child(aac)
        aaca = ModelFile("aaca", False)
        aaca.local_size = 100
        aac.add_child(aaca)
        ab = ModelFile("ab", True)
        ab.local_size = 100
        a.add_child(ab)
        aba = ModelFile("aba", False)
        aba.local_size = 100
        ab.add_child(aba)
        ac = ModelFile("ac", False)
        ac.local_size = 100
        a.add_child(ac)

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(a)
        while self.listener.extract_completed.call_count < 1:
            pass
        self.listener.extract_completed.assert_called_once_with("a")

        golden_calls = {
            (
                os.path.join(self.local_path, "a", "aa", "aaa"),
                os.path.join(self.out_dir_path, "a", "aa")
            ),
            (
                os.path.join(self.local_path, "a", "aa", "aac", "aaca"),
                os.path.join(self.out_dir_path, "a", "aa", "aac")
            ),
            (
                os.path.join(self.local_path, "a", "ab", "aba"),
                os.path.join(self.out_dir_path, "a", "ab")
            ),
        }
        self.assertEqual(3, self.mock_extract_archive.call_count)
        self.assertEqual(golden_calls, self.actual_calls)

    @timeout_decorator.timeout(2)
    def test_extract_dir_exits_command_early_on_shutdown(self):
        # Send extract dir command with two archives
        # Call shutdown after first extract but before second
        # Verify second extract is not called
        self.mock_is_archive.return_value = True

        self.call_stop = False

        def _extract_archive(**kwargs):
            print(kwargs)
            self.call_stop = True
            time.sleep(0.5)  # wait a bit so shutdown is called

        self.mock_extract_archive.side_effect = _extract_archive

        a = ModelFile("a", True)
        a.local_size = 200
        aa = ModelFile("aa", False)
        aa.local_size = 100
        a.add_child(aa)
        ab = ModelFile("ab", False)
        ab.local_size = 100
        a.add_child(ab)

        self.dispatch.add_listener(self.listener)
        self.dispatch.extract(a)

        while not self.call_stop:
            pass
        self.dispatch.stop()

        while self.mock_extract_archive.call_count < 1 \
                or self.listener.extract_failed.call_count < 1:
            pass
        self.listener.extract_completed.assert_not_called()
        self.listener.extract_failed.assert_called_once_with("a")
        self.assertEqual(1, self.mock_extract_archive.call_count)
