# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import os
import tempfile
import shutil
import getpass
import sys
import copy
import time
from filecmp import dircmp, cmp

import timeout_decorator

from common import overrides, PylftpContext
from controller import Controller
from model import ModelFile, IModelListener


class DummyListener(IModelListener):
    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        pass

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        pass

    @overrides(IModelListener)
    def file_removed(self, file: ModelFile):
        pass


# noinspection SpellCheckingInspection
class TestController(unittest.TestCase):
    maxDiff = None
    temp_dir = None

    @staticmethod
    def my_mkdir(*args):
        os.mkdir(os.path.join(TestController.temp_dir, *args))

    @staticmethod
    def my_touch(size, *args):
        path = os.path.join(TestController.temp_dir, *args)
        with open(path, 'wb') as f:
            f.write(bytearray([0xff] * size))

    @overrides(unittest.TestCase)
    def setUp(self):
        # Create a temp directory
        TestController.temp_dir = tempfile.mkdtemp(prefix="test_controller")

        # Create a bunch of files and directories
        # remote
        #   ra [dir]
        #     raa [file, 1*1024 bytes]
        #     rab [dir]
        #       raba [file, 5*1024 bytes]
        #       rabb [file, 2*1024 bytes]
        #   rb [dir]
        #     rba [file, 4*1024 bytes]
        #     rbb [file, 5*1024 bytes]
        #   rc [file, 10*1024 bytes]
        # local
        #   la [dir]
        #      laa [file, 1*1024 bytes]
        #      lab [file, 1*1024 bytes]
        #   lb [file, 2*1024 bytes]
        TestController.my_mkdir("remote")
        TestController.my_mkdir("remote", "ra")
        TestController.my_touch(1*1024, "remote", "ra", "raa")
        TestController.my_mkdir("remote", "ra", "rab")
        TestController.my_touch(5*1024, "remote", "ra", "rab", "raba")
        TestController.my_touch(2*1024, "remote", "ra", "rab", "rabb")
        TestController.my_mkdir("remote", "rb")
        TestController.my_touch(4*1024, "remote", "rb", "rba")
        TestController.my_touch(5*1024, "remote", "rb", "rbb")
        TestController.my_touch(10*1024, "remote", "rc")
        TestController.my_mkdir("local")
        TestController.my_mkdir("local", "la")
        TestController.my_touch(1*1024, "local", "la", "laa")
        TestController.my_touch(1*1024, "local", "la", "lab")
        TestController.my_touch(2*1024, "local", "lb")

        # Helper object to store the intial state
        f_ra = ModelFile("ra", True)
        f_ra.remote_size = 8*1024
        f_raa = ModelFile("raa", False)
        f_raa.remote_size = 1*1024
        f_ra.add_child(f_raa)
        f_rab = ModelFile("rab", True)
        f_rab.remote_size = 7*1024
        f_ra.add_child(f_rab)
        f_raba = ModelFile("raba", False)
        f_raba.remote_size = 5*1024
        f_rab.add_child(f_raba)
        f_rabb = ModelFile("rabb", False)
        f_rabb.remote_size = 2*1024
        f_rab.add_child(f_rabb)
        f_rb = ModelFile("rb", True)
        f_rb.remote_size = 9*1024
        f_rba = ModelFile("rba", False)
        f_rba.remote_size = 4*1024
        f_rb.add_child(f_rba)
        f_rbb = ModelFile("rbb", False)
        f_rbb.remote_size = 5*1024
        f_rb.add_child(f_rbb)
        f_rc = ModelFile("rc", False)
        f_rc.remote_size = 10*1024
        f_la = ModelFile("la", True)
        f_la.local_size = 2*1024
        f_laa = ModelFile("laa", False)
        f_laa.local_size = 1*1024
        f_la.add_child(f_laa)
        f_lab = ModelFile("lab", False)
        f_lab.local_size = 1*1024
        f_la.add_child(f_lab)
        f_lb = ModelFile("lb", False)
        f_lb.local_size = 2*1024

        self.initial_state = {f.name: f for f in [f_ra, f_rb, f_rc, f_la, f_lb]}

        # config file
        # Note: password-less ssh needs to be setup
        #       i.e. user's public key needs to be in authorized_keys
        #       cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.abspath(os.path.join(current_dir_path, "..", "..", ".."))
        self.config_file = open(os.path.join(self.temp_dir, "config"), "w")
        self.config_file.write("""
        [Lftp]
        remote_address=localhost
        remote_username={username}
        remote_path={remote_path}
        local_path={local_path}
        remote_path_to_scan_script={path_to_scan_script}
        num_max_parallel_downloads=2
        num_max_parallel_files_per_download=3
        num_max_connections_per_file=4
        
        [Controller]
        interval_ms_remote_scan=100
        interval_ms_local_scan=100
        """.format(
            username=getpass.getuser(),
            remote_path=os.path.join(self.temp_dir, "remote"),
            local_path=os.path.join(self.temp_dir, "local"),
            path_to_scan_script=script_path,
        ))
        self.config_file.flush()

        # patterns file
        self.patterns_file = open(os.path.join(self.temp_dir, "patterns"), "w")
        self.patterns_file.write("pattern1")
        self.patterns_file.flush()

        # backup sys.argv
        self.sys_argv_orig = copy.deepcopy(sys.argv)

        # Create context and controller
        sys.argv.append("-p")
        sys.argv.append(self.patterns_file.name)
        sys.argv.append("-c")
        sys.argv.append(self.config_file.name)
        sys.argv.append("-d")
        context = PylftpContext()
        self.controller = Controller(context)

    @overrides(unittest.TestCase)
    def tearDown(self):
        self.controller.exit()

        self.config_file.close()
        self.patterns_file.close()

        # Restore the original sys argv
        sys.argv = self.sys_argv_orig

        # Cleanup
        shutil.rmtree(self.temp_dir)

    def test_initial_model(self):
        time.sleep(0.5)
        self.controller.process()

        model_files = self.controller.get_model_files()
        self.assertEqual(len(self.initial_state.keys()), len(model_files))
        files_dict = {f.name: f for f in model_files}
        self.assertEqual(self.initial_state.keys(), files_dict.keys())
        for filename in self.initial_state.keys():
            # Note: put items in a list for a better diff output
            self.assertEqual([self.initial_state[filename]], [files_dict[filename]],
                             "Mismatch in file: {}".format(filename))

    def test_local_file_added(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Add a local file
        TestController.my_touch(1515, "local", "lnew")

        # Verify
        time.sleep(0.5)
        self.controller.process()
        lnew = ModelFile("lnew", False)
        lnew.local_size = 1515
        listener.file_added.assert_called_once_with(lnew)
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_local_file_updated(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Update a local file
        TestController.my_touch(1717, "local", "lb")

        # Verify
        time.sleep(0.5)
        self.controller.process()
        lb_old = ModelFile("lb", False)
        lb_old.local_size = 2*1024
        lb_new = ModelFile("lb", False)
        lb_new.local_size = 1717
        listener.file_updated.assert_called_once_with(lb_old, lb_new)
        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_local_file_removed(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Remove the local file
        os.remove(os.path.join(TestController.temp_dir, "local", "lb"))

        # Verify
        time.sleep(0.5)
        self.controller.process()
        lb = ModelFile("lb", False)
        lb.local_size = 2*1024
        listener.file_removed.assert_called_once_with(lb)
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()

    def test_remote_file_added(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Add a local file
        TestController.my_touch(1515, "remote", "rnew")

        # Verify
        time.sleep(0.5)
        self.controller.process()
        rnew = ModelFile("rnew", False)
        rnew.remote_size = 1515
        listener.file_added.assert_called_once_with(rnew)
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_remote_file_updated(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Update a local file
        TestController.my_touch(1717, "remote", "rc")

        # Verify
        time.sleep(0.5)
        self.controller.process()
        rc_old = ModelFile("rc", False)
        rc_old.remote_size = 10*1024
        rc_new = ModelFile("rc", False)
        rc_new.remote_size = 1717
        listener.file_updated.assert_called_once_with(rc_old, rc_new)
        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_remote_file_removed(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Remove the local file
        os.remove(os.path.join(TestController.temp_dir, "remote", "rc"))

        # Verify
        time.sleep(0.5)
        self.controller.process()
        rc = ModelFile("rc", False)
        rc.remote_size = 10*1024
        listener.file_removed.assert_called_once_with(rc)
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()

    @timeout_decorator.timeout(5)
    def test_command_queue_directory(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        # Process until done
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("ra", new_file.name)
                if new_file.local_size == 8*1024:
                    break
            time.sleep(0.5)

        # Verify
        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        dcmp = dircmp(os.path.join(TestController.temp_dir, "remote", "ra"),
                      os.path.join(TestController.temp_dir, "local", "ra"))
        self.assertFalse(dcmp.left_only)
        self.assertFalse(dcmp.right_only)
        self.assertFalse(dcmp.diff_files)

    @timeout_decorator.timeout(5)
    def test_command_queue_file(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))
        # Process until done
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rc", new_file.name)
                if new_file.local_size == 10*1024:
                    break
            time.sleep(0.5)

        # Verify
        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        fcmp = cmp(os.path.join(TestController.temp_dir, "remote", "rc"),
                   os.path.join(TestController.temp_dir, "local", "rc"))
        self.assertTrue(fcmp)

    @timeout_decorator.timeout(5)
    def test_command_queue_invalid(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "invaliddir"))
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_command_queue_local_directory(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "la"))
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()

    def test_command_queue_local_file(self):
        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "lb"))
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()

    @timeout_decorator.timeout(10)
    def test_command_stop_directory(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("ra", new_file.name)
                if new_file.local_size and new_file.local_size > 0:
                    break
            time.sleep(0.5)

        # Now stop the download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "ra"))
        self.controller.process()
        time.sleep(0.5)

        # Verify
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("ra", new_file.name)
        self.assertEqual(ModelFile.State.DEFAULT, new_file.state)
        self.assertLess(new_file.local_size, new_file.remote_size)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()

    @timeout_decorator.timeout(10)
    def test_command_stop_file(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rc", new_file.name)
                if new_file.local_size and new_file.local_size > 0:
                    break
            time.sleep(0.5)

        # Now stop the download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "rc"))
        self.controller.process()
        time.sleep(0.5)

        # Verify
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("rc", new_file.name)
        self.assertEqual(ModelFile.State.DEFAULT, new_file.state)
        self.assertLess(new_file.local_size, new_file.remote_size)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()

    @timeout_decorator.timeout(5)
    def test_command_stop_wrong(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("ra", new_file.name)
                if new_file.local_size and new_file.local_size > 0:
                    break
            time.sleep(0.5)

        # Now stop the download with wrong name
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "rb"))
        self.controller.process()
        time.sleep(1.0)

        # Verify that downloading is still going
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("ra", new_file.name)
        self.assertEqual(ModelFile.State.DOWNLOADING, new_file.state)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()

    @timeout_decorator.timeout(5)
    def test_command_stop_invalid(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(0.5)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("ra", new_file.name)
                if new_file.local_size and new_file.local_size > 0:
                    break
            time.sleep(0.5)

        # Now stop the download with wrong name
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "invalidfile"))
        self.controller.process()
        time.sleep(1.0)

        # Verify that downloading is still going
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("ra", new_file.name)
        self.assertEqual(ModelFile.State.DOWNLOADING, new_file.state)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
