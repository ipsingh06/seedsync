# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
from abc import ABC, abstractmethod
from multiprocessing import Process, Queue, Event
import queue
import time
from datetime import datetime
from typing import List
import signal
import threading

import tblib.pickling_support

from common import overrides, ServiceExit, MultiprocessingLogger
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
        self.__name = scanner.__class__.__name__
        super().__init__(name=self.__name)

        self.mp_logger = None
        self.logger = logging.getLogger(self.__name)
        self.__queue = queue_
        self.__scanner = scanner
        self.__interval_in_ms = interval_in_ms
        self.__exception_queue = Queue()
        self.verbose = verbose
        self.__terminate = Event()

    def set_multiprocessing_logger(self, mp_logger: MultiprocessingLogger):
        self.mp_logger = mp_logger

    def __signal(self, signum: int, _):
        # noinspection PyUnresolvedReferences
        # Signals is a generated enum
        self.logger.debug("Process caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()

    @overrides(Process)
    def run(self):
        # Replace the signal handlers that may have been set by main process
        # NOTE: very important that all signal handlers are reset
        #       otherwise we may be executing non process-safe code
        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.__signal)
        signal.signal(signal.SIGINT, self.__signal)

        # Set the thread name for convenience
        threading.current_thread().name = self.__name

        # Configure the logger for this process
        if self.mp_logger:
            self.logger = self.mp_logger.get_process_safe_logger().getChild(self.__name)

        # Set the base logger for scanner
        self.__scanner.set_base_logger(self.logger)

        self.logger.debug("Started scanner process")

        try:
            while not self.__terminate.is_set():
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
            self.logger.debug("ScannerProcess received a ServiceExit")
        except Exception as e:
            self.__exception_queue.put(ExceptionWrapper(e))
            raise

        self.logger.debug("Exiting scanner process")

    @overrides(Process)
    def terminate(self):
        self.__terminate.set()
        super().terminate()

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
