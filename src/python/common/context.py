# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
import copy
import argparse
from logging.handlers import RotatingFileHandler

# my libs
from .config import PylftpConfig
from .patterns import Patterns
from .constants import Constants


class PylftpContext:
    """
    Stores contextual information for the entire application
    """
    def __init__(self):
        """
        Primary constructor to construct the top-level context
        """
        # Parse arguments
        self.args = self._parse_args()

        # Logger setup
        # We separate the main log from the web-access log
        self.logger = self._create_logger(name=Constants.SERVICE_NAME,
                                          debug=self.args.debug,
                                          logdir=self.args.logdir)
        self.web_access_logger = self._create_logger(name=Constants.WEB_ACCESS_LOG_NAME,
                                                     debug=self.args.debug,
                                                     logdir=self.args.logdir)

        # Config
        self.config = PylftpConfig.from_file(self.args.config)

        # Patterns
        self.patterns = Patterns.from_file(self.args.patterns)

    def create_child_context(self, context_name: str) -> "PylftpContext":
        child_context = copy.copy(self)
        child_context.logger = self.logger.getChild(context_name)
        return child_context

    @staticmethod
    def _parse_args():
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("-c", "--config", required=True, help="Path to config file")
        parser.add_argument("-p", "--patterns", required=True, help="Path to patterns file")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")
        return parser.parse_args()

    @staticmethod
    def _create_logger(name: str, debug: bool, logdir: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        if logdir is not None:
            # Output logs to a file in the given directory
            handler = RotatingFileHandler(
                        "{}/{}.log".format(logdir, name),
                        maxBytes=Constants.MAX_LOG_SIZE_IN_BYTES,
                        backupCount=Constants.LOG_BACKUP_COUNT
                      )
        else:
            handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def print_to_log(self):
        # Print the config
        self.logger.debug("Config:")
        for section in self.config.dict.keys():
            for option in self.config.dict[section].keys():
                value = self.config.dict[section][option]
                self.logger.debug("  {}.{}: {}".format(section, option, value))

        # Print the patterns
        self.logger.debug("Patterns:")
        for pattern in self.patterns.content:
            self.logger.debug("  {}".format(pattern))
