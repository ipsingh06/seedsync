# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from abc import ABC, abstractmethod
from multiprocessing import Process, Queue
import time
from datetime import datetime
from typing import List

# my libs
from common import overrides, ServiceExit
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


class ScannerResult:
    """
    Results of a system scan
    """
    def __init__(self, timestamp: datetime, files: List[SystemFile]):
        self.timestamp = timestamp
        self.files = files


class ScannerProcess(Process):
    """
    Process to scan a file system and publish the result
    """
    def __init__(self, queue: Queue, scanner: IScanner, interval_in_ms: int):
        """
        Create a scanner process
        :param queue: multiprocessing.Queue in which to push results
        :param scanner: IScanner implementation
        :param interval_in_ms: Minimum interval (in ms) between results
        """
        super().__init__()
        self.logger = logging.getLogger("ScannerProcess")
        self.__queue = queue
        self.__scanner = scanner
        self.__interval_in_ms = interval_in_ms

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("ScannerProcess")

    @overrides(Process)
    def run(self):
        try:
            while True:
                timestamp_start = datetime.now()
                self.logger.debug("Running a scan")
                files = self.__scanner.scan()
                result = ScannerResult(timestamp=timestamp_start,
                                       files=files)
                self.__queue.put(result)
                delta_in_ms = int((datetime.now() - timestamp_start).total_seconds()*1000)
                if delta_in_ms < self.__interval_in_ms:
                    time.sleep(float(self.__interval_in_ms-delta_in_ms)/1000.0)
        except ServiceExit:
            self.logger.info("Exiting scanner process")
