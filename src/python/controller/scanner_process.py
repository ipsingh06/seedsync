# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
from abc import ABC, abstractmethod
from multiprocessing import Process, Queue
import queue
import time
from datetime import datetime
from typing import List

import tblib.pickling_support

from common import overrides, ServiceExit
from system import SystemFile


tblib.pickling_support.install()


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


class ExceptionWrapper:
    """
    An exception wrapper that works across processes
    Source: https://stackoverflow.com/a/26096355/8571324
    """
    def __init__(self, ee):
        self.ee = ee
        __,  __, self.tb = sys.exc_info()

    def re_raise(self):
        raise self.ee.with_traceback(self.tb)


class ScannerProcess(Process):
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
        super().__init__()
        self.logger = logging.getLogger("ScannerProcess")
        self.__queue = queue_
        self.__scanner = scanner
        self.__interval_in_ms = interval_in_ms
        self.__exception_queue = Queue()
        self.verbose = verbose

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("ScannerProcess")

    @overrides(Process)
    def run(self):
        try:
            while True:
                timestamp_start = datetime.now()
                if self.verbose:
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
        except Exception as e:
            self.__exception_queue.put(ExceptionWrapper(e))
            raise

    def propagate_exception(self):
        """
        Raises any exception that was caught by the process
        :return:
        """
        try:
            exc = self.__exception_queue.get(block=False)
            raise exc.re_raise()
        except queue.Empty:
            pass
