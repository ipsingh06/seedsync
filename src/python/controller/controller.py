# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import List
import multiprocessing
import queue
import logging
import pickle
from threading import Lock
from queue import Queue
from enum import Enum
import copy

# my libs
from .scanner_process import IScanner, ScannerProcess
from .model_builder import ModelBuilder
from common import overrides, PylftpJob, PylftpContext
from system import SystemFile, SystemScanner
from ssh import Ssh
from model import ModelError, ModelFile, Model, ModelDiff, ModelDiffUtil, IModelListener
from lftp import Lftp, LftpError


class ControllerJob(PylftpJob):
    """
    The Pylftp service
    Handles querying and downloading of files
    """
    def __init__(self, context: PylftpContext, controller: "Controller"):
        super().__init__(name=self.__class__.__name__, context=context)
        self.__context = context
        self.__controller = controller

    @overrides(PylftpJob)
    def setup(self):
        pass

    @overrides(PylftpJob)
    def execute(self):
        self.__controller.process()

    @overrides(PylftpJob)
    def cleanup(self):
        pass


class LocalScanner(IScanner):
    """
    Scanner implementation to scan the local filesystem
    """
    def __init__(self, local_path: str):
        self.__scanner = SystemScanner(local_path)

    def set_base_logger(self, base_logger: logging.Logger):
        pass

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        return self.__scanner.scan()


class RemoteScanner(IScanner):
    """
    Scanner implementation to scan the remote filesystem
    """
    def __init__(self,
                 remote_address: str,
                 remote_username: str,
                 remote_path_to_scan: str,
                 remote_path_to_scan_script: str):
        self.__remote_path_to_scan = remote_path_to_scan
        self.__ssh = Ssh(host=remote_address,
                         user=remote_username,
                         target_dir=remote_path_to_scan_script)

    def set_base_logger(self, base_logger: logging.Logger):
        self.__ssh.set_base_logger(base_logger)

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        out = self.__ssh.run_command("python3 scan_fs.py {}".format(self.__remote_path_to_scan))
        remote_files = pickle.loads(out)
        return remote_files


class Controller:
    """
    Top-level class that controls the behaviour of pylftp
    """
    class Command:
        class Action(Enum):
            QUEUE = 0
            STOP = 1

        def __init__(self, action: Action, filename: str):
            self.action = action
            self.filename = filename

    def __init__(self, context: PylftpContext):
        self.__context = context
        self.logger = context.logger.getChild("Controller")

        # The command queue
        self.__command_queue = Queue()

        # The model
        self.__model = Model()
        self.__model.set_base_logger(self.logger)
        # Lock for the model
        # Note: While the scanners are in a separate process, the rest of the application
        #       is threaded in a single process. (The webserver is bottle+paste which is
        #       multi-threaded). Therefore it is safe to use a threading Lock for the model
        #       (the scanner processes never try to access the model)
        self.__model_lock = Lock()

        # Model builder
        self.__model_builder = ModelBuilder()
        self.__model_builder.set_base_logger(self.logger)

        # Lftp
        self.__lftp = Lftp(address=self.__context.config.lftp.remote_address,
                           user=self.__context.config.lftp.remote_username,
                           password="")
        self.__lftp.set_base_logger(self.logger)
        self.__lftp.set_base_remote_dir_path(self.__context.config.lftp.remote_path)
        self.__lftp.set_base_local_dir_path(self.__context.config.lftp.local_path)

        # Setup the scanners and scanner processes
        self.__local_scanner = LocalScanner(self.__context.config.lftp.local_path)
        self.__remote_scanner = RemoteScanner(
            remote_address=self.__context.config.lftp.remote_address,
            remote_username=self.__context.config.lftp.remote_username,
            remote_path_to_scan=self.__context.config.lftp.remote_path,
            remote_path_to_scan_script=self.__context.config.lftp.remote_path_to_scan_script
        )
        self.__local_scanner.set_base_logger(self.logger.getChild("Local"))  # to differentiate scanner
        self.__remote_scanner.set_base_logger(self.logger.getChild("Remote"))  # to differentiate scanner

        self.__local_scan_queue = multiprocessing.Queue()
        self.__remote_scan_queue = multiprocessing.Queue()

        self.__local_scan_process = ScannerProcess(
            queue=self.__local_scan_queue,
            scanner=self.__local_scanner,
            interval_in_ms=self.__context.config.controller.interval_ms_local_scan
        )
        self.__remote_scan_process = ScannerProcess(
            queue=self.__remote_scan_queue,
            scanner=self.__remote_scanner,
            interval_in_ms=self.__context.config.controller.interval_ms_remote_scan
        )
        self.__local_scan_process.set_base_logger(self.logger.getChild("Local"))  # to differentiate scanner
        self.__remote_scan_process.set_base_logger(self.logger.getChild("Remote"))  # to differentiate scanner
        self.__local_scan_process.start()
        self.__remote_scan_process.start()

    def process(self):
        """
        Advance the controller state
        This method should return relatively quickly as the heavy lifting is done by concurrent tasks
        :return:
        """
        self.__process_commands()
        self.__update_model()

    def exit(self):
        self.__local_scan_process.terminate()
        self.__remote_scan_process.terminate()

    def get_model_files(self) -> List[ModelFile]:
        """
        Returns a copy of all the model files
        :return:
        """
        # Lock the model
        self.__model_lock.acquire()
        model_files = self.__get_model_files()
        # Release the model
        self.__model_lock.release()
        return model_files

    def add_model_listener(self, listener: IModelListener):
        """
        Adds a listener to the controller's model
        :param listener:
        :return:
        """
        # Lock the model
        self.__model_lock.acquire()
        self.__model.add_listener(listener)
        # Release the model
        self.__model_lock.release()

    def remove_model_listener(self, listener: IModelListener):
        """
        Removes a listener from the controller's model
        :param listener:
        :return:
        """
        # Lock the model
        self.__model_lock.acquire()
        self.__model.remove_listener(listener)
        # Release the model
        self.__model_lock.release()

    def get_model_files_and_add_listener(self, listener: IModelListener):
        """
        Adds a listener and returns the current state of model files in one atomic operation
        This guarantees that model update events are not missed or duplicated for the clients
        Without an atomic operation, the following scenarios can happen:
            1. get_model() -> model updated -> add_listener()
               The model update never propagates to client
            2. add_listener() -> model updated -> get_model()
               The model update is duplicated on client side (once through listener, and once
               through the model).
        :param listener:
        :return:
        """
        # Lock the model
        self.__model_lock.acquire()
        self.__model.add_listener(listener)
        model_files = self.__get_model_files()
        # Release the model
        self.__model_lock.release()
        return model_files

    def queue_command(self, command: Command):
        self.__command_queue.put(command)

    def __get_model_files(self) -> List[ModelFile]:
        model_files = []
        for filename in self.__model.get_file_names():
            model_files.append(copy.deepcopy(self.__model.get_file(filename)))
        return model_files

    def __update_model(self):
        # Grab the latest remote scan result
        latest_remote_scan = None
        try:
            while True:
                latest_remote_scan = self.__remote_scan_queue.get(block=False)
        except queue.Empty:
            pass

        # Grab the latest local scan result
        latest_local_scan = None
        try:
            while True:
                latest_local_scan = self.__local_scan_queue.get(block=False)
        except queue.Empty:
            pass

        # Grab the Lftp status
        lftp_statuses = None
        try:
            lftp_statuses = self.__lftp.status()
        except LftpError as e:
            self.logger.warn("Caught lftp error: {}".format(str(e)))

        # Build the new model
        if latest_remote_scan is not None:
            self.__model_builder.set_remote_files(latest_remote_scan.files)
        if latest_local_scan is not None:
            self.__model_builder.set_local_files(latest_local_scan.files)
        if lftp_statuses is not None:
            self.__model_builder.set_lftp_statuses(lftp_statuses)
        new_model = self.__model_builder.build_model()

        # Lock the model
        self.__model_lock.acquire()

        # Diff the new model with old model
        model_diff = ModelDiffUtil.diff_models(self.__model, new_model)

        # Apply changes to the new model
        for diff in model_diff:
            if diff.change == ModelDiff.Change.ADDED:
                self.__model.add_file(diff.new_file)
            elif diff.change == ModelDiff.Change.REMOVED:
                self.__model.remove_file(diff.old_file.name)
            elif diff.change == ModelDiff.Change.UPDATED:
                self.__model.update_file(diff.new_file)

        # Release the model
        self.__model_lock.release()

    def __process_commands(self):
        while not self.__command_queue.empty():
            command = self.__command_queue.get()
            self.logger.info("Received command {} for file {}".format(str(command.action), command.filename))
            try:
                file = self.__model.get_file(command.filename)
            except ModelError:
                self.logger.warn("Command failed. File {} does not exist in model".format(command.filename))
                return

            if command.action == Controller.Command.Action.QUEUE:
                if file.remote_size is None:
                    self.logger.warn("Command {} failed. File {} does not exist on remote".format(
                        str(command.action),
                        command.filename
                    ))
                    return
                try:
                    self.__lftp.queue(file.name, file.is_dir)
                except LftpError as e:
                    self.logger.warn("Caught lftp error: {}".format(str(e)))
            elif command.action == Controller.Command.Action.STOP:
                if file.state != ModelFile.State.DOWNLOADING:
                    self.logger.warn("Command {} failed. File {} is not downloading".format(
                        str(command.action),
                        command.filename
                    ))
                    return
                try:
                    self.__lftp.kill(file.name)
                except LftpError as e:
                    self.logger.warn("Caught lftp error: {}".format(str(e)))
