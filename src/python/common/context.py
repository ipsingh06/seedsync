# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import copy

# my libs
from .config import PylftpConfig


class PylftpArgs:
    """
    Container for args
    These are settings that aren't part of config but still needed by
    sub-components
    """
    def __init__(self):
        self.local_path_to_scanfs = None


class PylftpContext:
    """
    Stores contextual information for the entire application
    """
    def __init__(self,
                 logger: logging.Logger,
                 web_access_logger: logging.Logger,
                 config: PylftpConfig,
                 args: PylftpArgs):
        """
        Primary constructor to construct the top-level context
        """
        # Config
        self.logger = logger
        self.web_access_logger = web_access_logger
        self.config = config
        self.args = args

    def create_child_context(self, context_name: str) -> "PylftpContext":
        child_context = copy.copy(self)
        child_context.logger = self.logger.getChild(context_name)
        return child_context

    def print_to_log(self):
        # Print the config
        self.logger.debug("Config:")
        config_dict = self.config.as_dict()
        for section in config_dict.keys():
            for option in config_dict[section].keys():
                value = config_dict[section][option]
                self.logger.debug("  {}.{}: {}".format(section, option, value))

        self.logger.debug("Args:")
        self.logger.debug("  {}: {}".format("local_path_to_scanfs", self.args.local_path_to_scanfs))
