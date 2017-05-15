# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import threading
import time


class PylftpContext:
    """
    Stores contextual information for the entire application
    """
    def __init__(self, args, logger: logging.Logger):
        self.args = args
        self.logger = logger

    def create_child_context(self, context_name: str) -> "PylftpContext":
        return PylftpContext(
            args=self.args,
            logger=self.logger.getChild(context_name)
        )


class PylftpJob(threading.Thread):
    """
    Job thread that handles graceful shutdown
    """
    def __init__(self, name: str, context: PylftpContext):
        super().__init__()
        self.name = name
        self.logger = context.logger

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

    def run(self):
        self.logger.debug("Thread {} started".format(self.name))

        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            # TODO: let subclass define this behaviour somehow?
            time.sleep(0.5)

        # ... Clean shutdown code here ...
        self.logger.debug("Thread {} stopped".format(self.name))

    def terminate(self):
        """
        Mark job for termination
        :return: 
        """
        self.shutdown_flag.set()
