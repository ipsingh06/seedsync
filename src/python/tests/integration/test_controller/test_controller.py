# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import os
import tempfile
import shutil
import getpass
import time
from filecmp import dircmp, cmp
import logging
import sys

import timeout_decorator

from common import overrides, PylftpContext, PylftpConfig, PylftpArgs, PylftpError
from controller import Controller, ControllerPersist
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


class DummyCommandCallback(Controller.Command.ICallback):
    @overrides(Controller.Command.ICallback)
    def on_failure(self, error: str):
        pass

    @overrides(Controller.Command.ICallback)
    def on_success(self):
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

        # We also need to create an executable that the controller can install on remote
        # Since we don't have a packaged scanfs executable here, we simply
        # create an sh script that points to the python script
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        local_script_path = os.path.abspath(os.path.join(current_dir_path, "..", "..", "..", "scan_fs.py"))
        local_exe_path = os.path.join(TestController.temp_dir, "scanfs_local")
        remote_exe_path = os.path.join(TestController.temp_dir, "scanfs")
        with open(local_exe_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("python3 {} $*".format(local_script_path))
        os.chmod(local_exe_path, 0o775)
        ctx_args = PylftpArgs()
        ctx_args.local_path_to_scanfs = local_exe_path

        config_dict = {
            "General": {
                "debug": "True"
            },
            "Lftp": {
                "remote_address": "localhost",
                "remote_username": getpass.getuser(),
                "remote_path": os.path.join(self.temp_dir, "remote"),
                "local_path": os.path.join(self.temp_dir, "local"),
                "remote_path_to_scan_script": remote_exe_path,
                "num_max_parallel_downloads": "1",
                "num_max_parallel_files_per_download": "3",
                "num_max_connections_per_root_file": "4",
                "num_max_connections_per_dir_file": "4",
                "num_max_total_connections": "12",
            },
            "Controller": {
                "interval_ms_remote_scan": "100",
                "interval_ms_local_scan": "100",
                "interval_ms_downloading_scan": "100",
            },
            "Web": {
                "port": "8800",
            }
        }

        logger = logging.getLogger(TestController.__name__)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.context = PylftpContext(logger=logger,
                                     web_access_logger=logger,
                                     config=PylftpConfig.from_dict(config_dict),
                                     args=ctx_args)
        self.controller_persist = ControllerPersist()
        self.controller = None

    @overrides(unittest.TestCase)
    def tearDown(self):
        if self.controller:
            self.controller.exit()

        # Cleanup
        shutil.rmtree(self.temp_dir)

    def test_bad_config_doesnot_raise_ctor_exception(self):
        self.context.config.lftp.remote_address = "<bad>"
        self.context.config.lftp.remote_username = "<bad>"
        self.context.config.lftp.remote_path = "<bad>"
        self.context.config.lftp.local_path = "<bad>"
        self.context.config.lftp.remote_path_to_scan_script = "<bad>"
        # noinspection PyBroadException
        try:
            self.controller = Controller(self.context, self.controller_persist)
        except Exception:
            self.fail("Controller ctor raised exception unexpectedly")

    def test_bad_config_remote_address_raises_exception(self):
        self.context.config.lftp.remote_address = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(0.5)
        with self.assertRaises(PylftpError):
            self.controller.process()

    def test_bad_config_remote_username_raises_exception(self):
        self.context.config.lftp.remote_username = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(0.5)
        with self.assertRaises(PylftpError):
            self.controller.process()

    def test_bad_config_remote_path_raises_exception(self):
        self.context.config.lftp.remote_path = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(0.5)
        with self.assertRaises(PylftpError):
            self.controller.process()

    def test_bad_config_local_path_raises_exception(self):
        self.context.config.lftp.local_path = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(0.5)
        with self.assertRaises(PylftpError):
            self.controller.process()

    def test_bad_config_remote_path_to_scan_script_raises_exception(self):
        self.context.config.lftp.remote_path_to_scan_script = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(0.5)
        with self.assertRaises(PylftpError):
            self.controller.process()

    def test_initial_model(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)
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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

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
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "ra")
        command.add_callback(callback)
        self.controller.queue_command(command)
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
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        dcmp = dircmp(os.path.join(TestController.temp_dir, "remote", "ra"),
                      os.path.join(TestController.temp_dir, "local", "ra"))
        self.assertFalse(dcmp.left_only)
        self.assertFalse(dcmp.right_only)
        self.assertFalse(dcmp.diff_files)

    @timeout_decorator.timeout(5)
    def test_command_queue_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "rc")
        command.add_callback(callback)
        self.controller.queue_command(command)
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
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        fcmp = cmp(os.path.join(TestController.temp_dir, "remote", "rc"),
                   os.path.join(TestController.temp_dir, "local", "rc"))
        self.assertTrue(fcmp)

    @timeout_decorator.timeout(5)
    def test_command_queue_invalid(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "invaliddir")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()

        # Verify
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'invaliddir' not found", error)

    def test_command_queue_local_directory(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "la")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'la' does not exist remotely", error)

    def test_command_queue_local_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "lb")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until done
        self.controller.process()
        time.sleep(0.5)
        self.controller.process()
        listener.file_added.assert_not_called()
        listener.file_updated.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'lb' does not exist remotely", error)

    @timeout_decorator.timeout(10)
    def test_command_stop_directory(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "ra")
        command.add_callback(callback)
        self.controller.queue_command(command)
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
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

    @timeout_decorator.timeout(10)
    def test_command_stop_file(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue a download
        command = Controller.Command(Controller.Command.Action.QUEUE, "rc")
        command.add_callback(callback)
        self.controller.queue_command(command)
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
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

    @timeout_decorator.timeout(10)
    def test_command_stop_default(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Verify that rc is Default
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DEFAULT, files_dict["rc"].state)

        # Now stop the download
        command = Controller.Command(Controller.Command.Action.STOP, "rc")
        command.add_callback(callback)
        self.controller.queue_command(command)
        self.controller.process()

        # Verify nothing happened
        listener.file_updated.assert_not_called()
        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'rc' is not Queued or Downloading", error)

    @timeout_decorator.timeout(10)
    def test_command_stop_queued(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

        # Queue two downloads
        # This one will be Downloading
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))
        # This one will be Queued
        command = Controller.Command(Controller.Command.Action.QUEUE, "rb")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                if new_file.name == "rc" and new_file.local_size and new_file.local_size > 0:
                    break
            time.sleep(0.5)

        # Verify that rb is Queued
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.QUEUED, files_dict["rb"].state)

        # Now stop the download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "rb"))
        self.controller.process()
        time.sleep(0.5)

        # Verify that rc is Downloading, rb is Default
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["rc"].state)
        self.assertEqual(ModelFile.State.DEFAULT, files_dict["rb"].state)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

    @timeout_decorator.timeout(5)
    def test_command_stop_wrong(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

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
        command = Controller.Command(Controller.Command.Action.STOP, "rb")
        command.add_callback(callback)
        self.controller.queue_command(command)
        self.controller.process()
        time.sleep(1.0)

        # Verify that downloading is still going
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("ra", new_file.name)
        self.assertEqual(ModelFile.State.DOWNLOADING, new_file.state)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'rb' is not Queued or Downloading", error)

    @timeout_decorator.timeout(5)
    def test_command_stop_invalid(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()
        callback = DummyCommandCallback()
        callback.on_success = MagicMock()
        callback.on_failure = MagicMock()

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
        command = Controller.Command(Controller.Command.Action.STOP, "invalidfile")
        command.add_callback(callback)
        self.controller.queue_command(command)
        self.controller.process()
        time.sleep(1.0)

        # Verify that downloading is still going
        call = listener.file_updated.call_args
        new_file = call[0][1]
        self.assertEqual("ra", new_file.name)
        self.assertEqual(ModelFile.State.DOWNLOADING, new_file.state)

        listener.file_added.assert_not_called()
        listener.file_removed.assert_not_called()
        callback.on_success.assert_not_called()
        self.assertEqual(1, len(callback.on_failure.call_args_list))
        error = callback.on_failure.call_args[0][0]
        self.assertEqual("File 'invalidfile' not found", error)

    @timeout_decorator.timeout(5)
    def test_config_num_max_parallel_downloads(self):
        self.context.config.lftp.num_max_parallel_downloads = 2
        new_controller = Controller(self.context, ControllerPersist())

        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        new_controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        new_controller.add_model_listener(listener)
        new_controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue 3 downloads
        new_controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        new_controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rb"))
        new_controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))

        # Process until 2 downloads starts
        ra_downloading = False
        rb_downloading = False

        # noinspection PyUnusedLocal
        def updated_side_effect(old_file: ModelFile, new_file: ModelFile):
            nonlocal ra_downloading, rb_downloading
            if new_file.local_size and new_file.local_size > 0:
                if new_file.name == "ra":
                    ra_downloading = True
                elif new_file.name == "rb":
                    rb_downloading = True
            return
        listener.file_updated.side_effect = updated_side_effect
        while True:
            new_controller.process()
            if ra_downloading and rb_downloading:
                break

        # Verify that ra, rb is Downloading, rc is Queued
        files = new_controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["rb"].state)
        self.assertEqual(ModelFile.State.QUEUED, files_dict["rc"].state)

        new_controller.exit()

    @timeout_decorator.timeout(5)
    def test_downloading_scan(self):
        # Test that downloading scan is independent of local scan
        # Set a very large local scan interval and verify that downloading
        # updates are still propagated
        self.context.config.controller.interval_ms_downloading_scan = 200
        self.context.config.controller.interval_ms_local_scan = 10000
        new_controller = Controller(self.context, ControllerPersist())

        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        new_controller._Controller__lftp.rate_limit = 100

        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        new_controller.add_model_listener(listener)
        new_controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        new_controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))

        # Process until the downloads starts
        ra_downloading = False

        # noinspection PyUnusedLocal
        def updated_side_effect(old_file: ModelFile, new_file: ModelFile):
            nonlocal ra_downloading
            if new_file.local_size and new_file.local_size > 0:
                if new_file.name == "ra":
                    ra_downloading = True
            return
        listener.file_updated.side_effect = updated_side_effect
        while True:
            new_controller.process()
            if ra_downloading:
                break

        # Verify that ra is Downloading
        files = new_controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)

        new_controller.exit()

    @timeout_decorator.timeout(10)
    def test_persist_downloaded(self):
        self.controller = Controller(self.context, self.controller_persist)
        time.sleep(1.0)

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Verify empty download state
        self.assertEqual(0, len(self.controller_persist.downloaded_file_names))

        # Download rc
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))

        # Process until the downloads starts
        rc_downloaded = False

        # noinspection PyUnusedLocal
        def updated_side_effect(old_file: ModelFile, new_file: ModelFile):
            nonlocal rc_downloaded
            if new_file.state == ModelFile.State.DOWNLOADED and new_file.name == "rc":
                    rc_downloaded = True
            return
        listener.file_updated.side_effect = updated_side_effect
        while True:
            self.controller.process()
            if rc_downloaded:
                break

        self.assertTrue(rc_downloaded)
        # Verify downloaded state was persisted
        self.assertTrue("rc" in self.controller_persist.downloaded_file_names)

    @timeout_decorator.timeout(5)
    def test_redownload_deleted_file(self):
        # Test that a previously downloaded then deleted file can be redownloaded
        # We set the downloaded state in controller persist
        self.controller_persist.downloaded_file_names.add("ra")
        new_controller = Controller(self.context, self.controller_persist)

        time.sleep(1.0)

        # Verify that ra is marked as Deleted
        new_controller.process()
        files = new_controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DELETED, files_dict["ra"].state)

        # Ignore the initial state
        listener = DummyListener()
        new_controller.add_model_listener(listener)
        new_controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue a download
        new_controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))

        # Process until the downloads starts
        ra_downloading = False

        # noinspection PyUnusedLocal
        def updated_side_effect(old_file: ModelFile, new_file: ModelFile):
            nonlocal ra_downloading
            if new_file.local_size and new_file.local_size > 0:
                if new_file.name == "ra":
                    ra_downloading = True
            return
        listener.file_updated.side_effect = updated_side_effect
        while True:
            new_controller.process()
            if ra_downloading:
                break

        # Verify that ra is Downloading
        files = new_controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)

        new_controller.exit()
