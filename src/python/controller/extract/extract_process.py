# Copyright 2017, Inderpreet Singh, All rights reserved.

import multiprocessing
import datetime
import time
import queue
from typing import Optional, List
import logging

from .dispatch import ExtractDispatch, ExtractStatus, ExtractListener, ExtractDispatchError
from common import overrides, AppProcess
from model import ModelFile


class ExtractStatusResult:
    def __init__(self, timestamp: datetime, statuses: List[ExtractStatus]):
        self.timestamp = timestamp
        self.statuses = statuses


class ExtractCompletedResult:
    def __init__(self, timestamp: datetime, name: str, is_dir: bool):
        self.timestamp = timestamp
        self.name = name
        self.is_dir = is_dir


class ExtractProcess(AppProcess):
    __DEFAULT_SLEEP_INTERVAL_IN_SECS = 0.5

    class __ExtractListener(ExtractListener):
        def __init__(self, logger: logging.Logger, completed_queue: multiprocessing.Queue):
            self.logger = logger
            self.completed_queue = completed_queue

        def extract_completed(self, name: str, is_dir: bool):
            self.logger.info("Extraction completed for {}".format(name))
            completed_result = ExtractCompletedResult(timestamp=datetime.datetime.now(),
                                                      name=name,
                                                      is_dir=is_dir)
            self.completed_queue.put(completed_result)

        def extract_failed(self, name: str, is_dir: bool):
            self.logger.error("Extraction failed for {}".format(name))

    def __init__(self, out_dir_path: str, local_path: str):
        super().__init__(name=self.__class__.__name__)
        self.__out_dir_path = out_dir_path
        self.__local_path = local_path
        self.__command_queue = multiprocessing.Queue()
        self.__status_result_queue = multiprocessing.Queue()
        self.__completed_result_queue = multiprocessing.Queue()
        self.__dispatch = None

    @overrides(AppProcess)
    def run_init(self):
        # Create dispatch inside the process
        self.__dispatch = ExtractDispatch(out_dir_path=self.__out_dir_path,
                                          local_path=self.__local_path)

        # Add extract listener
        listener = ExtractProcess.__ExtractListener(
            logger=self.logger,
            completed_queue=self.__completed_result_queue
        )
        self.__dispatch.add_listener(listener)

        # Start dispatch
        self.__dispatch.start()

    @overrides(AppProcess)
    def run_cleanup(self):
        self.__dispatch.stop()

    @overrides(AppProcess)
    def run_loop(self):
        # Forward all the extract commands
        try:
            while True:
                file = self.__command_queue.get(block=False)
                try:
                    self.__dispatch.extract(file)
                except ExtractDispatchError as e:
                    self.logger.warning(str(e))
        except queue.Empty:
            pass

        # Queue the latest status
        statuses = self.__dispatch.status()
        status_result = ExtractStatusResult(timestamp=datetime.datetime.now(),
                                            statuses=statuses)
        self.__status_result_queue.put(status_result)

        time.sleep(ExtractProcess.__DEFAULT_SLEEP_INTERVAL_IN_SECS)

    def extract(self, file: ModelFile):
        """
        Process-safe method to queue an extraction
        :param file:
        :return:
        """
        self.__command_queue.put(file)

    def pop_latest_statuses(self) -> Optional[ExtractStatusResult]:
        """
        Process-safe method to retrieve latest extract status
        Returns none if no new status is available since the last time
        this method was called
        :return:
        """
        latest_result = None
        try:
            while True:
                latest_result = self.__status_result_queue.get(block=False)
        except queue.Empty:
            pass
        return latest_result

    def pop_completed(self) -> List[ExtractCompletedResult]:
        """
        Process-safe method to retrieve list of newly completed extractions
        Returns an empty list if no new extractions were completed since the
        last time this method was called.
        :return:
        """
        completed = []
        try:
            while True:
                result = self.__completed_result_queue.get(block=False)
                completed.append(result)
        except queue.Empty:
            pass
        return completed
