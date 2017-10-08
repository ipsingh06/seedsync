# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
import copy
from logging.handlers import RotatingFileHandler
from typing import Optional

# my libs
from .config import PylftpConfig
from .constants import Constants


class PylftpContext:
    """
    Stores contextual information for the entire application
    """
    def __init__(self,
                 debug: bool,
                 logdir: Optional[str],
                 config: PylftpConfig):
        """
        Primary constructor to construct the top-level context
        """
        # Logger setup
        # We separate the main log from the web-access log
        self.logger = self._create_logger(name=Constants.SERVICE_NAME,
                                          debug=debug,
                                          logdir=logdir)
        self.web_access_logger = self._create_logger(name=Constants.WEB_ACCESS_LOG_NAME,
                                                     debug=debug,
                                                     logdir=logdir)

        # Config
        self.config = config

    def create_child_context(self, context_name: str) -> "PylftpContext":
        child_context = copy.copy(self)
        child_context.logger = self.logger.getChild(context_name)
        return child_context

    @staticmethod
    def _create_logger(name: str, debug: bool, logdir: Optional[str]) -> logging.Logger:
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
        config_dict = self.config.as_dict()
        for section in config_dict.keys():
            for option in config_dict[section].keys():
                value = config_dict[section][option]
                self.logger.debug("  {}.{}: {}".format(section, option, value))
