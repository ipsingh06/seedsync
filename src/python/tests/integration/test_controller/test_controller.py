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
import zipfile
import subprocess
from datetime import datetime

import timeout_decorator

from common import overrides, Context, Config, Args, AppError, Localization, Status
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
    __KEEP_FILES = False  # for debugging

    maxDiff = None
    temp_dir = None
    work_dir = None

    @staticmethod
    def my_mkdir(*args):
        os.mkdir(os.path.join(TestController.temp_dir, *args))

    @staticmethod
    def my_touch(size, *args):
        path = os.path.join(TestController.temp_dir, *args)
        with open(path, 'wb') as f:
            f.write(bytearray([0xff] * size))

    @staticmethod
    def create_archive(*args):
        """
        Creates a archive of a text file containing name of archive
        The text file is named "<archive.ext>.txt"
        Returns archive file size
        """
        path = os.path.join(TestController.temp_dir, *args)
        archive_name = os.path.basename(path)
        temp_file_path = os.path.join(TestController.work_dir, archive_name+".txt")
        with open(temp_file_path, "w") as f:
            f.write(os.path.basename(path))

        ext = os.path.splitext(os.path.basename(path))[1]
        ext = ext[1:]
        if ext == "zip":
            zf = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
            zf.write(temp_file_path, os.path.basename(temp_file_path))
            zf.close()
        elif ext == "rar":
            subprocess.Popen(["rar",
                              "a",
                              "-ep",
                              path,
                              temp_file_path]).communicate()
        else:
            raise ValueError("Unsupported archive format: {}".format(os.path.basename(path)))
        return os.path.getsize(path)

    @overrides(unittest.TestCase)
    def setUp(self):
        # Create a temp directory
        TestController.temp_dir = tempfile.mkdtemp(prefix="test_controller")

        # Create a work directory for temp files
        TestController.work_dir = os.path.join(TestController.temp_dir, "work")
        os.mkdir(TestController.work_dir)

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

        # Also create some archives
        # Store the true archive file sizes in a dict
        # remote
        #   rd [dir]
        #     rd.zip [file]
        #   re.rar [file]
        #   rf [dir]
        #     rfa [dir]
        #       rfa.zip [file]
        #     rfb [dir]
        #       rfb.zip [file]
        # local
        #   lc [dir]
        #     lca.rar [file]
        #     lcb.zip [file]
        self.archive_sizes = {}
        TestController.my_mkdir("remote", "rd")
        self.archive_sizes["rd.zip"] = TestController.create_archive("remote", "rd", "rd.zip")
        self.archive_sizes["re.rar"] = TestController.create_archive("remote", "re.rar")
        TestController.my_mkdir("remote", "rf")
        TestController.my_mkdir("remote", "rf", "rfa")
        self.archive_sizes["rfa.zip"] = TestController.create_archive("remote", "rf", "rfa", "rfa.zip")
        TestController.my_mkdir("remote", "rf", "rfb")
        self.archive_sizes["rfb.zip"] = TestController.create_archive("remote", "rf", "rfb", "rfb.zip")
        TestController.my_mkdir("local", "lc")
        self.archive_sizes["lca.rar"] = TestController.create_archive("local", "lc", "lca.rar")
        self.archive_sizes["lcb.zip"] = TestController.create_archive("local", "lc", "lcb.zip")

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

        f_rd = ModelFile("rd", True)
        f_rd.remote_size = self.archive_sizes["rd.zip"]
        f_rd.is_extractable = True
        f_rdx = ModelFile("rd.zip", False)
        f_rdx.remote_size = self.archive_sizes["rd.zip"]
        f_rdx.is_extractable = True
        f_rd.add_child(f_rdx)
        f_re = ModelFile("re.rar", False)
        f_re.remote_size = self.archive_sizes["re.rar"]
        f_re.is_extractable = True
        f_rf = ModelFile("rf", True)
        f_rf.remote_size = self.archive_sizes["rfa.zip"] + self.archive_sizes["rfb.zip"]
        f_rf.is_extractable = True
        f_rfa = ModelFile("rfa", True)
        f_rfa.remote_size = self.archive_sizes["rfa.zip"]
        f_rfa.is_extractable = True
        f_rfax = ModelFile("rfa.zip", False)
        f_rfax.remote_size = self.archive_sizes["rfa.zip"]
        f_rfax.is_extractable = True
        f_rfa.add_child(f_rfax)
        f_rf.add_child(f_rfa)
        f_rfb = ModelFile("rfb", True)
        f_rfb.remote_size = self.archive_sizes["rfb.zip"]
        f_rfb.is_extractable = True
        f_rf.add_child(f_rfb)
        f_rfbx = ModelFile("rfb.zip", False)
        f_rfbx.remote_size = self.archive_sizes["rfb.zip"]
        f_rfbx.is_extractable = True
        f_rfb.add_child(f_rfbx)

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

        f_lc = ModelFile("lc", True)
        f_lc.local_size = self.archive_sizes["lca.rar"] + self.archive_sizes["lcb.zip"]
        f_lc.is_extractable = True
        f_lca = ModelFile("lca.rar", False)
        f_lca.local_size = self.archive_sizes["lca.rar"]
        f_lca.is_extractable = True
        f_lc.add_child(f_lca)
        f_lcb = ModelFile("lcb.zip", False)
        f_lcb.local_size = self.archive_sizes["lcb.zip"]
        f_lcb.is_extractable = True
        f_lc.add_child(f_lcb)

        self.initial_state = {f.name: f for f in [
            f_ra, f_rb, f_rc, f_rd, f_re, f_rf,
            f_la, f_lb, f_lc
        ]}

        # config file
        # Note: password-less ssh needs to be setup
        #       i.e. user's public key needs to be in authorized_keys
        #       cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

        # We also need to create an executable that the controller can install on remote
        # Since we don't have a packaged scanfs executable here, we simply
        # create an sh script that points to the python script
        # Note: the executable must be the venv one so any custom imports work
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        local_script_path = os.path.abspath(os.path.join(current_dir_path, "..", "..", "..", "scan_fs.py"))
        local_exe_path = os.path.join(TestController.temp_dir, "scanfs_local")
        remote_exe_path = os.path.join(TestController.temp_dir, "scanfs")
        with open(local_exe_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("{} {} $*".format(sys.executable, local_script_path))
        os.chmod(local_exe_path, 0o775)
        ctx_args = Args()
        ctx_args.local_path_to_scanfs = local_exe_path

        config_dict = {
            "General": {
                "debug": "True",
                "verbose": "True"
            },
            "Lftp": {
                "remote_address": "localhost",
                "remote_username": getpass.getuser(),
                "remote_port": 22,
                "remote_path": os.path.join(self.temp_dir, "remote"),
                "local_path": os.path.join(self.temp_dir, "local"),
                "remote_path_to_scan_script": remote_exe_path,
                "num_max_parallel_downloads": "1",
                "num_max_parallel_files_per_download": "3",
                "num_max_connections_per_root_file": "4",
                "num_max_connections_per_dir_file": "4",
                "num_max_total_connections": "12",
                "use_temp_file": "False"
            },
            "Controller": {
                "interval_ms_remote_scan": "100",
                "interval_ms_local_scan": "100",
                "interval_ms_downloading_scan": "100",
                "extract_path": "/unused/path",
                "use_local_path_as_extract_path": True
            },
            "Web": {
                "port": "8800",
            },
            "AutoQueue": {
                "enabled": "True",
                "patterns_only": "True",
                "auto_extract": "True"
            }
        }

        logger = logging.getLogger(TestController.__name__)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.context = Context(logger=logger,
                               web_access_logger=logger,
                               config=Config.from_dict(config_dict),
                               args=ctx_args,
                               status=Status())
        self.controller_persist = ControllerPersist()
        self.controller = None

    @overrides(unittest.TestCase)
    def tearDown(self):
        if self.controller:
            self.controller.exit()

        # Cleanup
        if not TestController.__KEEP_FILES:
            shutil.rmtree(self.temp_dir)

    # noinspection PyMethodMayBeStatic
    def __wait_for_initial_model(self):
        while len(self.controller.get_model_files()) < 5:
            time.sleep(0.1)
            self.controller.process()

    @timeout_decorator.timeout(20)
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

    @timeout_decorator.timeout(20)
    def test_bad_config_remote_address_raises_exception(self):
        self.context.config.lftp.remote_address = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnusedLocal
        with self.assertRaises(AppError) as error:
            while True:
                self.controller.process()
        # noinspection PyUnreachableCode
        self.assertEqual(Localization.Error.REMOTE_SERVER_INSTALL, str(error.exception))

    @timeout_decorator.timeout(20)
    def test_bad_config_remote_username_raises_exception(self):
        self.context.config.lftp.remote_username = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnusedLocal
        with self.assertRaises(AppError) as error:
            while True:
                self.controller.process()
        # noinspection PyUnreachableCode
        self.assertEqual(Localization.Error.REMOTE_SERVER_INSTALL, str(error.exception))

    @timeout_decorator.timeout(20)
    def test_bad_config_remote_path_raises_exception(self):
        self.context.config.lftp.remote_path = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnusedLocal
        with self.assertRaises(AppError) as error:
            while True:
                self.controller.process()
        # noinspection PyUnreachableCode
        self.assertEqual(Localization.Error.REMOTE_SERVER_SCAN, str(error.exception))

    @timeout_decorator.timeout(20)
    def test_bad_config_local_path_raises_exception(self):
        self.context.config.lftp.local_path = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnusedLocal
        with self.assertRaises(AppError) as error:
            while True:
                self.controller.process()
        # noinspection PyUnreachableCode
        self.assertEqual(Localization.Error.LOCAL_SERVER_SCAN, str(error.exception))

    @timeout_decorator.timeout(20)
    def test_bad_config_remote_path_to_scan_script_raises_exception(self):
        self.context.config.lftp.remote_path_to_scan_script = "<bad>"
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnusedLocal
        with self.assertRaises(AppError) as error:
            while True:
                self.controller.process()
        # noinspection PyUnreachableCode
        self.assertEqual(Localization.Error.REMOTE_SERVER_INSTALL, str(error.exception))

    @timeout_decorator.timeout(20)
    def test_initial_model(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

        model_files = self.controller.get_model_files()
        self.assertEqual(len(self.initial_state.keys()), len(model_files))
        files_dict = {f.name: f for f in model_files}
        self.assertEqual(self.initial_state.keys(), files_dict.keys())
        for filename in self.initial_state.keys():
            # Note: put items in a list for a better diff output
            self.assertEqual([self.initial_state[filename]], [files_dict[filename]],
                             "Mismatch in file: {}".format(filename))

    @timeout_decorator.timeout(20)
    def test_local_file_added(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_local_file_updated(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_local_file_removed(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_remote_file_added(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_remote_file_updated(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_remote_file_removed(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_queue_directory(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_queue_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_queue_invalid(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_queue_local_directory(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_queue_local_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_directory(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_file(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_default(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_queued(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_wrong(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_stop_invalid(self):
        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_command_extract_after_downloading_remote_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "re.rar")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("re.rar", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "re.rar")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("re.rar", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        # Verify
        re_txt_path = os.path.join(TestController.temp_dir, "local", "re.rar.txt")
        self.assertTrue(os.path.isfile(re_txt_path))
        with open(re_txt_path, "r") as f:
            self.assertEqual("re.rar", f.read())

    @timeout_decorator.timeout(20)
    def test_command_extract_after_downloading_remote_directory(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        # Verify
        rd_txt_path = os.path.join(TestController.temp_dir, "local", "rd", "rd.zip.txt")
        self.assertTrue(os.path.isfile(rd_txt_path))
        with open(rd_txt_path, "r") as f:
            self.assertEqual("rd.zip", f.read())

    @timeout_decorator.timeout(20)
    def test_command_extract_after_downloading_remote_directory_multilevel(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "rf")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rf", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "rf")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rf", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        # Verify
        rfa_txt_path = os.path.join(TestController.temp_dir, "local", "rf", "rfa", "rfa.zip.txt")
        self.assertTrue(os.path.isfile(rfa_txt_path))
        with open(rfa_txt_path, "r") as f:
            self.assertEqual("rfa.zip", f.read())
        rfb_txt_path = os.path.join(TestController.temp_dir, "local", "rf", "rfb", "rfb.zip.txt")
        self.assertTrue(os.path.isfile(rfb_txt_path))
        with open(rfb_txt_path, "r") as f:
            self.assertEqual("rfb.zip", f.read())

    @timeout_decorator.timeout(20)
    def test_command_extract_local_directory(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "lc")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        # Can't rely on state changes since final state is back to Default
        # Look for presence of extracted files
        lca_txt_path = os.path.join(TestController.temp_dir, "local", "lc", "lca.rar.txt")
        lcb_txt_path = os.path.join(TestController.temp_dir, "local", "lc", "lcb.zip.txt")
        while True:
            self.controller.process()
            if os.path.isfile(lca_txt_path) and os.path.isfile(lcb_txt_path):
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        # Verify
        with open(lca_txt_path, "r") as f:
            self.assertEqual("lca.rar", f.read())
        with open(lcb_txt_path, "r") as f:
            self.assertEqual("lcb.zip", f.read())

    @timeout_decorator.timeout(20)
    def test_command_reextract_after_extracting_remote_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "re.rar")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("re.rar", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "re.rar")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("re.rar", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_success.reset_mock()
        callback.on_failure.assert_not_called()

        # Verify
        re_txt_path = os.path.join(TestController.temp_dir, "local", "re.rar.txt")
        self.assertTrue(os.path.isfile(re_txt_path))
        with open(re_txt_path, "r") as f:
            self.assertEqual("re.rar", f.read())

        # Delete the extracted file
        os.remove(re_txt_path)
        self.assertFalse(os.path.isfile(re_txt_path))

        # Queue a re-extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "re.rar")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        # Can't rely on state changes since final state is back to Extracted
        # Look for presence of extracted file
        while True:
            self.controller.process()
            if os.path.isfile(re_txt_path):
                break
            time.sleep(0.5)

        # Verify again
        self.assertTrue(os.path.isfile(re_txt_path))
        with open(re_txt_path, "r") as f:
            self.assertEqual("re.rar", f.read())

    @timeout_decorator.timeout(20)
    def test_command_extract_remote_only_fails(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

        # wait for initial scan
        self.__wait_for_initial_model()

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
        self.assertEqual(ModelFile.State.DEFAULT, files_dict["re.rar"].state)

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "re.rar")
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
        self.assertEqual("File 're.rar' does not exist locally", error)

    @timeout_decorator.timeout(20)
    def test_command_extract_after_downloading_remote_directory_to_separate_path(self):
        # Change the extract path
        extract_path = os.path.join(TestController.temp_dir, "extract")
        os.mkdir(extract_path)
        self.context.config.controller.extract_path = extract_path
        self.context.config.controller.use_local_path_as_extract_path = False
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        # Verify
        rd_txt_path = os.path.join(extract_path, "rd", "rd.zip.txt")
        self.assertTrue(os.path.isfile(rd_txt_path))
        with open(rd_txt_path, "r") as f:
            self.assertEqual("rd.zip", f.read())

    @timeout_decorator.timeout(20)
    def test_command_redownload_after_deleting_extracted_file(self):
        """
        File is downloaded, then extracted, then deleted, then redownloaded
        Verify that final state is Downloaded and NOT Extracted
        """
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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
        command = Controller.Command(Controller.Command.Action.QUEUE, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.DOWNLOADED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        # Queue an extraction
        command = Controller.Command(Controller.Command.Action.EXTRACT, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until extract complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_success.reset_mock()
        callback.on_failure.assert_not_called()

        # Verify
        re_txt_path = os.path.join(TestController.temp_dir, "local", "rd", "rd.zip.txt")
        self.assertTrue(os.path.isfile(re_txt_path))
        with open(re_txt_path, "r") as f:
            self.assertEqual("rd.zip", f.read())

        # Delete the whole thing
        shutil.rmtree(os.path.join(TestController.temp_dir, "local", "rd"))

        # Process until deleted state
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                if new_file.state == ModelFile.State.DELETED:
                    break
            time.sleep(0.5)

        # Queue the download AGAIN
        command = Controller.Command(Controller.Command.Action.QUEUE, "rd")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download complete
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                self.assertEqual("rd", new_file.name)
                # EXTRACTED is wrong, but we check for that later on
                if new_file.state == ModelFile.State.DOWNLOADED or \
                        new_file.state == ModelFile.State.EXTRACTED:
                    break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()
        callback.on_success.reset_mock()

        time.sleep(0.5)
        self.controller.process()
        # Verify file is in DOWNLOADED state
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADED, files_dict["rd"].state)

    @timeout_decorator.timeout(20)
    def test_config_num_max_parallel_downloads(self):
        self.context.config.lftp.num_max_parallel_downloads = 2
        self.controller = Controller(self.context, ControllerPersist())
        self.controller.start()

        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

        # Ignore the initial state
        listener = DummyListener()
        self.controller.add_model_listener(listener)
        self.controller.process()

        # Setup mock
        listener.file_added = MagicMock()
        listener.file_updated = MagicMock()
        listener.file_removed = MagicMock()

        # Queue 3 downloads
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "ra"))
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rb"))
        self.controller.queue_command(Controller.Command(Controller.Command.Action.QUEUE, "rc"))

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
            self.controller.process()
            if ra_downloading and rb_downloading:
                break

        # Verify that ra, rb is Downloading, rc is Queued
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["rb"].state)
        self.assertEqual(ModelFile.State.QUEUED, files_dict["rc"].state)

    @timeout_decorator.timeout(20)
    def test_downloading_scan(self):
        # Test that downloading scan is independent of local scan
        # Set a very large local scan interval and verify that downloading
        # updates are still propagated
        self.context.config.controller.interval_ms_downloading_scan = 200
        self.context.config.controller.interval_ms_local_scan = 10000
        self.controller = Controller(self.context, ControllerPersist())
        self.controller.start()

        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

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
            self.controller.process()
            if ra_downloading:
                break

        # Verify that ra is Downloading
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)

    @timeout_decorator.timeout(20)
    def test_persist_downloaded(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

    @timeout_decorator.timeout(20)
    def test_redownload_deleted_file(self):
        # Test that a previously downloaded then deleted file can be redownloaded
        # We set the downloaded state in controller persist
        self.controller_persist.downloaded_file_names.add("ra")
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()

        # White box hack: limit the rate of lftp so download doesn't finish
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 100

        # wait for initial scan
        self.__wait_for_initial_model()

        # Verify that ra is marked as Deleted
        self.controller.process()
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DELETED, files_dict["ra"].state)

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
            self.controller.process()
            if ra_downloading:
                break

        # Verify that ra is Downloading
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["ra"].state)

    @timeout_decorator.timeout(20)
    def test_command_delete_local_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "local", "lb")
        self.assertTrue(os.path.isfile(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_LOCAL, "lb")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until file is removed from model
        while True:
            self.controller.process()
            call = listener.file_removed.call_args
            if call:
                file = call[0][0]
                self.assertEqual("lb", file.name)
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        self.assertFalse(os.path.exists(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_local_dir(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "local", "la")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_LOCAL, "la")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until file is removed from model
        while True:
            self.controller.process()
            call = listener.file_removed.call_args
            if call:
                file = call[0][0]
                self.assertEqual("la", file.name)
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        self.assertFalse(os.path.exists(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_remote_dir(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "remote", "ra")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_REMOTE, "ra")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until file is removed from model
        while True:
            self.controller.process()
            call = listener.file_removed.call_args
            if call:
                file = call[0][0]
                self.assertEqual("ra", file.name)
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        self.assertFalse(os.path.exists(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_local_fails_on_remote_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()

        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "remote", "ra")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_LOCAL, "ra")
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
        self.assertEqual("File 'ra' does not exist locally", error)

        self.assertTrue(os.path.isdir(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_remote_fails_on_local_file(self):
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()

        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "local", "la")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_REMOTE, "la")
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
        self.assertEqual("File 'la' does not exist remotely", error)

        self.assertTrue(os.path.isdir(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_remote_forces_immediate_rescan(self):
        # Test that after a remote delete a remote scan is immediately done
        # Test this by simply setting the remote scan interval to a really large value
        # that would timeout the test if it wasn't forced
        self.context.config.controller.interval_ms_remote_scan = 90000

        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "remote", "ra")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_REMOTE, "ra")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until file is removed from model
        while True:
            self.controller.process()
            call = listener.file_removed.call_args
            if call:
                file = call[0][0]
                self.assertEqual("ra", file.name)
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        self.assertFalse(os.path.exists(file_path))

    @timeout_decorator.timeout(20)
    def test_command_delete_local_forces_immediate_rescan(self):
        # Test that after a local delete a local scan is immediately done
        # Test this by simply setting the local scan interval to a really large value
        # that would timeout the test if it wasn't forced
        self.context.config.controller.interval_ms_local_scan = 90000

        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # wait for initial scan
        self.__wait_for_initial_model()

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

        file_path = os.path.join(TestController.temp_dir, "local", "la")
        self.assertTrue(os.path.isdir(file_path))

        # Send delete command
        command = Controller.Command(Controller.Command.Action.DELETE_LOCAL, "la")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until file is removed from model
        while True:
            self.controller.process()
            call = listener.file_removed.call_args
            if call:
                file = call[0][0]
                self.assertEqual("la", file.name)
                break
            time.sleep(0.5)
        callback.on_success.assert_called_once_with()
        callback.on_failure.assert_not_called()

        self.assertFalse(os.path.exists(file_path))

    @timeout_decorator.timeout(20)
    @unittest.skip
    def test_download_with_excessive_connections(self):
        # Note: this test sometimes crashes the dbus
        #       reset with: sudo systemctl restart systemd-logind

        # Test excessive connections and a large LFTP status output
        #     - large files names to blow up the status
        #     - large max num connections, connections per file
        #     - download many files in parallel
        def create_large_file(path, size):
            f = open(path, "wb")
            f.seek(size - 1)
            f.write(b"\0")
            f.close()
            print("File size: ", os.stat(path).st_size)

        # Create a bunch of large files that can be downloaded in chunks
        path = os.path.join(TestController.temp_dir, "remote", "large")
        local_path = os.path.join(TestController.temp_dir, "local", "large")
        os.mkdir(path)
        a_path = os.path.join(path, "a"*200 + ".txt")
        create_large_file(a_path, 20*1024*1024)
        b_path = os.path.join(path, "b"*200 + ".txt")
        create_large_file(b_path, 20*1024*1024)
        c_path = os.path.join(path, "c"*200 + ".txt")
        create_large_file(c_path, 20*1024*1024)
        d_path = os.path.join(path, "d"*200 + ".txt")
        create_large_file(d_path, 20*1024*1024)
        e_path = os.path.join(path, "e"*200 + ".txt")
        create_large_file(e_path, 20*1024*1024)
        f_path = os.path.join(path, "f"*200 + ".txt")
        create_large_file(f_path, 20*1024*1024)
        g_path = os.path.join(path, "g"*200 + ".txt")
        create_large_file(g_path, 20*1024*1024)
        h_path = os.path.join(path, "h"*200 + ".txt")
        create_large_file(h_path, 20*1024*1024)

        # White box hack: limit the rate of lftp so download doesn't finish
        #                 also set min-chunk size to a small value for lots of connections
        self.context.config.lftp.num_max_total_connections = 20
        self.context.config.lftp.num_max_connections_per_dir_file = 20
        self.context.config.lftp.num_max_parallel_files_per_download = 8

        # noinspection PyUnresolvedReferences
        self.controller = Controller(self.context, self.controller_persist)
        self.controller.start()
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.rate_limit = 5*1024
        # noinspection PyUnresolvedReferences
        self.controller._Controller__lftp.min_chunk_size = "10"

        # wait for initial scan
        self.__wait_for_initial_model()

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

        # Queue
        command = Controller.Command(Controller.Command.Action.QUEUE, "large")
        command.add_callback(callback)
        self.controller.queue_command(command)
        # Process until download starts
        while True:
            self.controller.process()
            call = listener.file_updated.call_args
            if call:
                new_file = call[0][1]
                if new_file.name == "large" and new_file.state == ModelFile.State.DOWNLOADING:
                    break
            time.sleep(0.5)

        # Wait for a bit so we start getting large statuses
        start_time = datetime.now()
        elapsed_secs = 0
        while elapsed_secs < 5:
            print("Elapsed secs: ", elapsed_secs)
            self.controller.process()
            time.sleep(0.5)
            elapsed_secs = (datetime.now()-start_time).total_seconds()

        # Verify that download is still ongoing
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DOWNLOADING, files_dict["large"].state)

        # Stop the download
        self.controller.queue_command(Controller.Command(Controller.Command.Action.STOP, "large"))
        self.controller.process()
        time.sleep(0.5)

        # Verify that download is stopped
        files = self.controller.get_model_files()
        files_dict = {f.name: f for f in files}
        self.assertEqual(ModelFile.State.DEFAULT, files_dict["large"].state)

        # Remove the files
        shutil.rmtree(path)
        shutil.rmtree(local_path)
