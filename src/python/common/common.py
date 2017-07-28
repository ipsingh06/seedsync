# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, List


# Custom types
Config = Dict[str, Dict[str, str]]
Patterns = List[str]


class PylftpError(Exception):
    """
    Exception indicating an error
    """
    pass


class PylftpContext:
    """
    Stores contextual information for the entire application
    """
    def __init__(self,
                 args,
                 logger: logging.Logger,
                 web_access_logger: logging.Logger,
                 config: Config,
                 patterns: Patterns):
        self.args = args
        self.logger = logger
        self.web_access_logger = web_access_logger
        self.config = config
        self.patterns = patterns

    def create_child_context(self, context_name: str) -> "PylftpContext":
        return PylftpContext(
            args=self.args,
            logger=self.logger.getChild(context_name),
            web_access_logger=self.web_access_logger,
            config=self.config,
            patterns=self.patterns
        )

    def print_to_log(self):
        # Print the config
        self.logger.debug("Config:")
        for section in self.config.keys():
            for option in self.config[section].keys():
                value = self.config[section][option]
                self.logger.debug("  {}.{}: {}".format(section, option, value))

        # Print the patterns
        self.logger.debug("Patterns:")
        for pattern in self.patterns:
            self.logger.debug("  {}".format(pattern))


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

    def run(self):
        self.logger.debug("Thread {} started".format(self.name))

        # ... Setup code here ...
        self.logger.debug("Calling setup for {}".format(self.name))
        self.setup()
        self.logger.debug("Finished setup for {}".format(self.name))

        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            self.execute()
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
