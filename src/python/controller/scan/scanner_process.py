# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from abc import ABC, abstractmethod
import multiprocessing
from datetime import datetime
from typing import List, Optional
import queue

from common import overrides, AppProcess, AppError
from system import SystemFile


class ScannerError(AppError):
    """
    Indicates a scanner error

    Args:
        recoverable: indicates scans can be retried
    """
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message)
        self.recoverable = recoverable


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
    def __init__(self,
                 timestamp: datetime,
                 files: List[SystemFile],
                 failed: bool = False,
                 error_message: str = None):
        self.timestamp = timestamp
        self.files = files
        self.failed = failed
        self.error_message = error_message


class ScannerProcess(AppProcess):
    """
    Process to scan a file system and publish the result
    """
    def __init__(self,
                 scanner: IScanner, interval_in_ms: int,
                 verbose: bool = True):
        """
        Create a scanner process
        :param scanner: IScanner implementation
        :param interval_in_ms: Minimum interval (in ms) between results
        """
        super().__init__(name=scanner.__class__.__name__)
        self.__queue = multiprocessing.Queue()
        self.__wake_event = multiprocessing.Event()
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
        try:
            files = self.__scanner.scan()
            result = ScannerResult(timestamp=timestamp_start,
                                   files=files)
        except ScannerError as e:
            # Non-recoverable errors continue up as a fatal error
            if not e.recoverable:
                raise
            result = ScannerResult(timestamp=timestamp_start,
                                   files=[],
                                   failed=True,
                                   error_message=str(e))
        self.__queue.put(result)
        delta_in_s = (datetime.now() - timestamp_start).total_seconds()
        delta_in_ms = int(delta_in_s * 1000)
        if self.verbose:
            self.logger.debug("Scan took {:.3f}s".format(delta_in_s))

        # Wait until the next interval, or until a wake event is fired
        if delta_in_ms < self.__interval_in_ms:
            wait_time_in_s = float(self.__interval_in_ms - delta_in_ms) / 1000.0
            self.__wake_event.wait(timeout=wait_time_in_s)
            self.__wake_event.clear()

    def pop_latest_result(self) -> Optional[ScannerResult]:
        """
        Process-safe method to retrieve latest scan result
        Returns None if no new scan result was generated since the last time
        this method was called
        :return:
        """
        latest_scan = None
        try:
            while True:
                latest_scan = self.__queue.get(block=False)
        except queue.Empty:
            pass
        return latest_scan

    def force_scan(self):
        """Force process to wake and do an immediate scan"""
        self.__wake_event.set()
