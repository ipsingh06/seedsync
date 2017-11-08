# Copyright 2017, Inderpreet Singh, All rights reserved.

import sys
import threading
import time
from abc import ABC, abstractmethod

# my libs
from .context import PylftpContext
from .types import overrides


class PylftpJob(threading.Thread, ABC):
    """
    Job thread that handles graceful shutdown
    """
    _DEFAULT_SLEEP_INTERVAL_IN_SECS = 0.5

    def __init__(self, name: str, context: PylftpContext):
        super().__init__()
        self.name = name
        self.logger = context.logger

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        # For exception propagation
        self.exc_info = None

    @overrides(threading.Thread)
    def run(self):
        self.logger.debug("Thread {} started".format(self.name))

        # ... Setup code here ...
        self.logger.debug("Calling setup for {}".format(self.name))
        self.setup()
        self.logger.debug("Finished setup for {}".format(self.name))

        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            # noinspection PyBroadException
            try:
                self.execute()
            except Exception as e:
                self.exc_info = sys.exc_info()
                self.logger.exception("Caught exception in job {}".format(self.name))
                # break out of run loop and proceed to cleanup
                self.shutdown_flag.set()
                break

            time.sleep(PylftpJob._DEFAULT_SLEEP_INTERVAL_IN_SECS)

        # ... Clean shutdown code here ...
        self.logger.debug("Calling cleanup for {}".format(self.name))
        self.cleanup()
        self.logger.debug("Finished cleanup for {}".format(self.name))

        self.logger.debug("Thread {} stopped".format(self.name))

    def terminate(self):
        """
        Mark job for termination
        :return:
        """
        self.shutdown_flag.set()

    def propagate_exception(self):
        """
        Raises any exception captured by this job in whatever thread calls this method
        Source: https://stackoverflow.com/a/1854263/8571324
        :return:
        """
        if self.exc_info:
            exc_info = self.exc_info
            self.exc_info = None
            raise exc_info[1].with_traceback(exc_info[2])

    @abstractmethod
    def setup(self):
        """
        Setup is run once when the job starts
        :return:
        """
        pass

    @abstractmethod
    def execute(self):
        """
        Execute is run repeatedly, separated by a sleep interval, while the job is running
        This method must return relatively quickly, otherwise the job won't be able to safely
        terminate
        :return:
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Cleanup is run one when the job is about to terminate
        :return:
        """
        pass
