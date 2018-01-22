# Copyright 2017, Inderpreet Singh, All rights reserved.

from enum import Enum
from typing import List
import queue
import logging
import os
import threading
import time
from abc import ABC, abstractmethod

from .extract import Extract, ExtractError
from model import ModelFile
from common import AppError


class ExtractDispatchError(AppError):
    pass


class ExtractListener(ABC):
    @abstractmethod
    def extract_completed(self, name: str):
        pass

    @abstractmethod
    def extract_failed(self, name: str):
        pass


class ExtractStatus:
    """
    Represents the status of a single extraction request
    """

    class State(Enum):
        EXTRACTING = 0

    def __init__(self, name: str, state: State):
        self.__name = name
        self.__state = state

    @property
    def name(self) -> str: return self.__name

    @property
    def state(self) -> State: return self.__state


class ExtractDispatch:

    __WORKER_SLEEP_INTERVAL_IN_SECS = 0.5

    class _Task:
        def __init__(self, root_name: str):
            self.root_name = root_name
            self.archive_paths = []  # list of (archive path, out path) pairs

        def add_archive(self, archive_path: str, out_dir_path: str):
            self.archive_paths.append((archive_path, out_dir_path))

    def __init__(self, out_dir_path: str, local_path: str):
        self.__out_dir_path = out_dir_path
        self.__local_path = local_path

        self.__task_queue = queue.Queue()
        self.__worker = threading.Thread(name="ExtractWorker",
                                         target=self.__worker)
        self.__worker_shutdown = threading.Event()

        self.__listeners = []
        self.__listeners_lock = threading.Lock()

        self.logger = logging.getLogger(self.__class__.__name__)

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild(self.__class__.__name__)

    def start(self):
        self.__worker.start()

    def stop(self):
        self.__worker_shutdown.set()
        self.__worker.join()

    def add_listener(self, listener: ExtractListener):
        self.__listeners_lock.acquire()
        self.__listeners.append(listener)
        self.__listeners_lock.release()

    def status(self) -> List[ExtractStatus]:
        pass

    def extract(self, model_file: ModelFile):
        # noinspection PyProtectedMember
        task = ExtractDispatch._Task(model_file.name)

        if model_file.is_dir:
            # For a directory, try and find all archives
            # Loop through all directories using BFS
            frontier = [model_file]
            while frontier:
                curr_file = frontier.pop(0)
                if curr_file.is_dir:
                    frontier += curr_file.get_children()
                else:
                    archive_full_path = os.path.join(self.__local_path, curr_file.full_path)
                    out_dir_path = os.path.join(self.__out_dir_path, os.path.dirname(curr_file.full_path))
                    if curr_file.local_size is not None \
                            and curr_file.local_size > 0 \
                            and Extract.is_archive(archive_full_path):
                        task.add_archive(archive_path=archive_full_path,
                                         out_dir_path=out_dir_path)
            # Verify that there was at least one archive file
            if len(task.archive_paths) > 0:
                self.__task_queue.put(task)
            else:
                raise ExtractDispatchError(
                    "Directory does not contain any archives: {}".format(model_file.name)
                )
        else:
            # For a single file, it must exist locally and must be an archive
            if model_file.local_size in (None, 0):
                raise ExtractDispatchError("File does not exist locally: {}".format(model_file.name))
            archive_full_path = os.path.join(self.__local_path, model_file.name)
            if not Extract.is_archive(archive_full_path):
                raise ExtractDispatchError("File is not an archive: {}".format(model_file.name))
            task.add_archive(archive_path=archive_full_path,
                             out_dir_path=self.__out_dir_path)
            self.__task_queue.put(task)

    def __worker(self):
        self.logger.debug("Started worker thread")

        while not self.__worker_shutdown.is_set():
            # Try to grab next task
            while True:
                try:
                    task = self.__task_queue.get(block=False)
                    # We have a task, extract archives one by one
                    completed = True

                    try:
                        for archive_path, out_dir_path in task.archive_paths:
                            if self.__worker_shutdown.is_set():
                                # exit early
                                self.logger.warning("Extraction failed, shutdown requested")
                                completed = False
                                break

                            Extract.extract_archive(
                                archive_path=archive_path,
                                out_dir_path=out_dir_path
                            )

                    except ExtractError:
                        self.logger.exception("Caught an extraction error")
                        completed = False

                    # Send notification to listeners
                    self.__listeners_lock.acquire()
                    for listener in self.__listeners:
                        if completed:
                            listener.extract_completed(task.root_name)
                        else:
                            listener.extract_failed(task.root_name)
                    self.__listeners_lock.release()

                except queue.Empty:
                    break

            time.sleep(ExtractDispatch.__WORKER_SLEEP_INTERVAL_IN_SECS)

        self.logger.debug("Stopped worker thread")
