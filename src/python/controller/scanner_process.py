# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from abc import ABC, abstractmethod
from multiprocessing import Queue
import time
from datetime import datetime
from typing import List

from common import overrides, AppProcess
from system import SystemFile


class IScanner(ABC):
    """
    Interface to scan the system.
    This hides the scanning implementation from the scanner process.
    """
    @abstractmethod
    def scan(self) -> List[SystemFile]:
        """Scan system"""
        pass

    @abstractmethod
    def set_base_logger(self, base_logger: logging.Logger):
        pass


class ScannerResult:
    """
    Results of a system scan
    """
    def __init__(self, timestamp: datetime, files: List[SystemFile]):
        self.timestamp = timestamp
        self.files = files


class ScannerProcess(AppProcess):
    """
    Process to scan a file system and publish the result
    """
    def __init__(self,
                 queue_: Queue,
                 scanner: IScanner, interval_in_ms: int,
                 verbose: bool = True):
        """
        Create a scanner process
        :param queue_: multiprocessing.Queue in which to push results
        :param scanner: IScanner implementation
        :param interval_in_ms: Minimum interval (in ms) between results
        """
        super().__init__(name=scanner.__class__.__name__)
        self.__queue = queue_
        self.__scanner = scanner
        self.__interval_in_ms = interval_in_ms
        self.verbose = verbose

    @overrides(AppProcess)
    def run_init(self):
        # Set the base logger for scanner
        self.__scanner.set_base_logger(self.logger)

    @overrides(AppProcess)
    def run_cleanup(self):
        pass

    @overrides(AppProcess)
    def run_loop(self):
        timestamp_start = datetime.now()
        if self.verbose:
            self.logger.debug("Running a scan")
        files = self.__scanner.scan()
        result = ScannerResult(timestamp=timestamp_start,
                               files=files)
        self.__queue.put(result)
        delta_in_s = (datetime.now() - timestamp_start).total_seconds()
        delta_in_ms = int(delta_in_s * 1000)
        if self.verbose:
            self.logger.debug("Scan took {:.3f}s".format(delta_in_s))
        if delta_in_ms < self.__interval_in_ms:
            time.sleep(float(self.__interval_in_ms - delta_in_ms) / 1000.0)
