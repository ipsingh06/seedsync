# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
from abc import abstractmethod
from multiprocessing import Process, Queue, Event
import queue
import signal
import threading
from datetime import datetime

import tblib.pickling_support

from common import overrides, ServiceExit, MultiprocessingLogger


tblib.pickling_support.install()


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


class AppProcess(Process):
    """
    Process with some additional functionality and fixes
      * Support for a multiprocessing logger
      * Removes signals to prevent join problems
      * Propagates exceptions to owner process
      * Safe terminate with timeout, followed by force terminate
    """

    # Timeout before process is force terminated
    __DEFAULT_TERMINATE_TIMEOUT_MS = 1000

    def __init__(self, name: str):
        self.__name = name
        super().__init__(name=self.__name)

        self.mp_logger = None
        self.logger = logging.getLogger(self.__name)
        self.__exception_queue = Queue()
        self.__terminate = Event()

    def set_multiprocessing_logger(self, mp_logger: MultiprocessingLogger):
        self.mp_logger = mp_logger

    @overrides(Process)
    def run(self):
        # Replace the signal handlers that may have been set by main process to
        # default handlers. Having non-default handlers in subprocesses causes
        # a deadlock when attempting to join the process
        # Info: https://stackoverflow.com/a/631605

        # NOTE: There is a minuscule chance of deadlock if a signal is received
        #       between start of the method and these resets.
        #       The ideal solution is to remove the signal before the process is
        #       started. Unfortunately that's difficult to do here because the
        #       subprocess is started from a job thread, and python doesn't
        #       allow setting signals from outside the main thread.
        #       So we accept this risk for the quick and easy solution here
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Set the thread name for convenience
        threading.current_thread().name = self.__name

        # Configure the logger for this process
        if self.mp_logger:
            self.logger = self.mp_logger.get_process_safe_logger().getChild(self.__name)

        self.logger.debug("Started process")

        self.run_init()

        try:
            while not self.__terminate.is_set():
                self.run_loop()
            self.logger.debug("Process received terminate flag")
        except ServiceExit:
            self.logger.debug("Process received a ServiceExit")
        except Exception as e:
            self.logger.debug("Process caught an exception")
            self.__exception_queue.put(ExceptionWrapper(e))
            raise
        finally:
            self.run_cleanup()

        self.logger.debug("Exiting process")

    @overrides(Process)
    def terminate(self):
        # Send a terminate signal, and force terminate after a timeout
        self.__terminate.set()

        def elapsed_ms(start):
            delta_in_s = (datetime.now() - start).total_seconds()
            delta_in_ms = int(delta_in_s * 1000)
            return delta_in_ms

        timestamp_start = datetime.now()
        while self.is_alive() and \
                elapsed_ms(timestamp_start) < AppProcess.__DEFAULT_TERMINATE_TIMEOUT_MS:
            pass

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

    @abstractmethod
    def run_init(self):
        """
        Called once before the run loop
        :return:
        """
        pass

    @abstractmethod
    def run_cleanup(self):
        """
        Called once before cleanup
        :return:
        """
        pass

    @abstractmethod
    def run_loop(self):
        """
        Process behaviour should be implemented here.
        This function is repeatedly called until process exits.
        The check for graceful shutdown is performed between the loop iterations,
        so try to limit the run time for this method.
        :return:
        """
        pass
