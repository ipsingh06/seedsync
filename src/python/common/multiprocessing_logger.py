# Copyright 2017, Inderpreet Singh, All rights reserved.

import multiprocessing
import threading
import queue
import logging
import time
import sys
from logging.handlers import QueueHandler


class MultiprocessingLogger:
    """
    A helper class to enable logging across processes
    It starts a listener thread on the main process. The listener thread
    receives records on a queue from other processes and sends them to the
    main logger (effectively serializing the logging).
    Other processes use a QueueHandler to send logging records to the
    listener thread on the main process.
    Source: https://gist.github.com/vsajip/820132
    """

    __LISTENER_SLEEP_INTERVAL_IN_SECS = 0.1

    def __init__(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("MPLogger")
        self.__queue = multiprocessing.Queue(-1)
        self.__logger_level = base_logger.level
        self.__listener = threading.Thread(target=self.__listener)
        self.__listener_shutdown = threading.Event()
        self.__listener_exc_info = None

    def start(self):
        self.__listener.start()

    def stop(self):
        self.__listener_shutdown.set()
        self.__listener.join()

    def propagate_exception(self):
        """
        Raises any exception captured by the listener thread
        Source: https://stackoverflow.com/a/1854263/8571324
        :return:
        """
        if self.__listener_exc_info:
            exc_info = self.__listener_exc_info
            self.__listener_exc_info = None
            raise exc_info[1].with_traceback(exc_info[2])

    def get_process_safe_logger(self) -> logging.Logger:
        """
        Returns a process-safe logger
        This logger sends all records to the main process
        :return:
        """
        queue_handler = QueueHandler(self.__queue)
        root_logger = logging.getLogger()

        # The fork may have happened after the root logger was setup by the main process
        # Remove all handlers from the root logger for this process
        handlers = root_logger.handlers[:]
        for handler in handlers:
            handler.close()
            root_logger.removeHandler(handler)

        root_logger.addHandler(queue_handler)
        root_logger.setLevel(self.__logger_level)
        return root_logger

    def __listener(self):
        self.logger.debug("Started listener thread")

        while not self.__listener_shutdown.is_set():
            # noinspection PyBroadException
            try:
                while True:
                    try:
                        record = self.__queue.get(block=False)
                        self.logger.getChild(record.name).handle(record)
                    except queue.Empty:
                        break
            except Exception:
                self.__listener_exc_info = sys.exc_info()
                self.logger.exception("Caught exception in listener thread")
                # break out of run loop
                self.__listener_shutdown.set()
                break

            time.sleep(MultiprocessingLogger.__LISTENER_SLEEP_INTERVAL_IN_SECS)

        self.logger.debug("Stopped listener thread")
