# Copyright 2017, Inderpreet Singh, All rights reserved.

from abc import ABC, abstractmethod
from typing import List
import multiprocessing
import queue
from threading import Lock
from queue import Queue
from enum import Enum
import copy

# my libs
from .scanner_process import ScannerProcess
from .model_builder import ModelBuilder
from common import PylftpContext
from model import ModelError, ModelFile, Model, ModelDiff, ModelDiffUtil, IModelListener
from lftp import Lftp, LftpError, LftpJobStatus
from .downloading_scanner import DownloadingScanner
from .local_scanner import LocalScanner
from .remote_scanner import RemoteScanner
from .controller_persist import ControllerPersist


class Controller:
    """
    Top-level class that controls the behaviour of pylftp
    """
    class Command:
        """
        Class by which clients of Controller can request Actions to be executed
        Supports callbacks by which clients can be notified of action success/failure
        Note: callbacks will be executed in Controller thread, so any heavy computation
              should be moved out of the callback
        """
        class Action(Enum):
            QUEUE = 0
            STOP = 1

        class ICallback(ABC):
            """Command callback interface"""
            @abstractmethod
            def on_success(self):
                """Called on successful completion of action"""
                pass

            @abstractmethod
            def on_failure(self, error: str):
                """Called on action failure"""
                pass

        def __init__(self, action: Action, filename: str):
            self.action = action
            self.filename = filename
            self.callbacks = []

        def add_callback(self, callback: ICallback):
            self.callbacks.append(callback)

    def __init__(self,
                 context: PylftpContext,
                 persist: ControllerPersist):
        self.__context = context
        self.__persist = persist
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
        self.__model_builder.set_downloaded_files(self.__persist.downloaded_file_names)

        # Lftp
        self.__lftp = Lftp(address=self.__context.config.lftp.remote_address,
                           user=self.__context.config.lftp.remote_username,
                           password="")
        self.__lftp.set_base_logger(self.logger)
        self.__lftp.set_base_remote_dir_path(self.__context.config.lftp.remote_path)
        self.__lftp.set_base_local_dir_path(self.__context.config.lftp.local_path)
        # Configure Lftp
        self.__lftp.num_parallel_jobs = self.__context.config.lftp.num_max_parallel_downloads
        self.__lftp.num_parallel_files = self.__context.config.lftp.num_max_parallel_files_per_download
        self.__lftp.num_connections = self.__context.config.lftp.num_max_connections_per_file

        # Setup the scanners and scanner processes
        self.__downloading_scanner = DownloadingScanner(self.__context.config.lftp.local_path)
        self.__local_scanner = LocalScanner(self.__context.config.lftp.local_path)
        self.__remote_scanner = RemoteScanner(
            remote_address=self.__context.config.lftp.remote_address,
            remote_username=self.__context.config.lftp.remote_username,
            remote_path_to_scan=self.__context.config.lftp.remote_path,
            remote_path_to_scan_script=self.__context.config.lftp.remote_path_to_scan_script
        )
        self.__downloading_scanner.set_base_logger(self.logger.getChild("Downloading"))  # to differentiate scanner
        self.__local_scanner.set_base_logger(self.logger.getChild("Local"))  # to differentiate scanner
        self.__remote_scanner.set_base_logger(self.logger.getChild("Remote"))  # to differentiate scanner

        self.__downloading_scan_queue = multiprocessing.Queue()
        self.__local_scan_queue = multiprocessing.Queue()
        self.__remote_scan_queue = multiprocessing.Queue()

        self.__downloading_scan_process = ScannerProcess(
            queue_=self.__downloading_scan_queue,
            scanner=self.__downloading_scanner,
            interval_in_ms=self.__context.config.controller.interval_ms_downloading_scan,
            verbose=False
        )
        self.__local_scan_process = ScannerProcess(
            queue_=self.__local_scan_queue,
            scanner=self.__local_scanner,
            interval_in_ms=self.__context.config.controller.interval_ms_local_scan,
        )
        self.__remote_scan_process = ScannerProcess(
            queue_=self.__remote_scan_queue,
            scanner=self.__remote_scanner,
            interval_in_ms=self.__context.config.controller.interval_ms_remote_scan,
        )
        self.__downloading_scan_process.set_base_logger(self.logger.getChild("Downloading"))  # to differentiate scanner
        self.__local_scan_process.set_base_logger(self.logger.getChild("Local"))  # to differentiate scanner
        self.__remote_scan_process.set_base_logger(self.logger.getChild("Remote"))  # to differentiate scanner
        self.__downloading_scan_process.start()
        self.__local_scan_process.start()
        self.__remote_scan_process.start()

    def process(self):
        """
        Advance the controller state
        This method should return relatively quickly as the heavy lifting is done by concurrent tasks
        :return:
        """
        self.__propagate_exceptions()
        self.__process_commands()
        self.__update_model()

    def exit(self):
        self.__downloading_scan_process.terminate()
        self.__local_scan_process.terminate()
        self.__remote_scan_process.terminate()
        self.logger.info("Exited controller")

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

        # Grab the latest downloading scan result
        latest_downloading_scan = None
        try:
            while True:
                latest_downloading_scan = self.__downloading_scan_queue.get(block=False)
        except queue.Empty:
            pass

        # Grab the Lftp status
        lftp_statuses = None
        try:
            lftp_statuses = self.__lftp.status()
        except LftpError as e:
            self.logger.warning("Caught lftp error: {}".format(str(e)))

        # Update the downloading scanner's state
        if lftp_statuses is not None:
            downloading_file_names = [s.name for s in lftp_statuses if s.state == LftpJobStatus.State.RUNNING]
            self.__downloading_scanner.set_downloading_files(downloading_file_names)

        # Build the new model
        if latest_remote_scan is not None:
            self.__model_builder.set_remote_files(latest_remote_scan.files)
        if latest_local_scan is not None:
            self.__model_builder.set_local_files(latest_local_scan.files)
        if latest_downloading_scan is not None:
            self.__model_builder.set_downloading_files(latest_downloading_scan.files)
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

            # Detect if a file was just Downloaded
            #   an Added file in Downloaded state
            #   an Updated file transitioning to Downloaded state
            # If so, update the persist state
            downloaded = False
            if diff.change == ModelDiff.Change.ADDED and \
                    diff.new_file.state == ModelFile.State.DOWNLOADED:
                downloaded = True
            elif diff.change == ModelDiff.Change.UPDATED and \
                    diff.new_file.state == ModelFile.State.DOWNLOADED and \
                    diff.old_file.state != ModelFile.State.DOWNLOADED:
                downloaded = True
            if downloaded:
                self.__persist.downloaded_file_names.add(diff.new_file.name)
                self.__model_builder.set_downloaded_files(self.__persist.downloaded_file_names)

        # Release the model
        self.__model_lock.release()

    def __process_commands(self):
        while not self.__command_queue.empty():
            command = self.__command_queue.get()
            self.logger.info("Received command {} for file {}".format(str(command.action), command.filename))
            try:
                file = self.__model.get_file(command.filename)
            except ModelError:
                self.logger.warning("Command failed. File {} does not exist in model".format(command.filename))
                for callback in command.callbacks:
                    callback.on_failure("File '{}' not found".format(command.filename))
                continue

            if command.action == Controller.Command.Action.QUEUE:
                if file.remote_size is None:
                    self.logger.warning("Command {} failed. File {} does not exist on remote".format(
                        str(command.action),
                        command.filename
                    ))
                    for callback in command.callbacks:
                        callback.on_failure("File '{}' does not exist remotely".format(command.filename))
                    continue
                try:
                    self.__lftp.queue(file.name, file.is_dir)
                except LftpError as e:
                    self.logger.warning("Caught lftp error: {}".format(str(e)))
                    for callback in command.callbacks:
                        callback.on_failure("Lftp error: ".format(str(e)))
                    continue
            elif command.action == Controller.Command.Action.STOP:
                if file.state not in (ModelFile.State.DOWNLOADING, ModelFile.State.QUEUED):
                    self.logger.warning("Command {} failed. File {} is not downloading or queued".format(
                        str(command.action),
                        command.filename
                    ))
                    for callback in command.callbacks:
                        callback.on_failure("File '{}' is not Queued or Downloading".format(command.filename))
                    continue
                try:
                    self.__lftp.kill(file.name)
                except LftpError as e:
                    self.logger.warning("Caught lftp error: {}".format(str(e)))
                    for callback in command.callbacks:
                        callback.on_failure("Lftp error: ".format(str(e)))
                    continue

            # If we get here, it was a success
            for callback in command.callbacks:
                callback.on_success()

    def __propagate_exceptions(self):
        """
        Propagate any exceptions from child processes/threads to this thread
        :return:
        """
        self.__downloading_scan_process.propagate_exception()
        self.__local_scan_process.propagate_exception()
        self.__remote_scan_process.propagate_exception()
