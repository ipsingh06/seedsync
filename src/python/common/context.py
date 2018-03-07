# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import copy
import collections

# my libs
from .config import Config
from .status import Status


class Args:
    """
    Container for args
    These are settings that aren't part of config but still needed by
    sub-components
    """
    def __init__(self):
        self.local_path_to_scanfs = None
        self.html_path = None
        self.debug = None
        self.exit = None

    def as_dict(self) -> dict:
        dct = collections.OrderedDict()
        dct["local_path_to_scanfs"] = str(self.local_path_to_scanfs)
        dct["html_path"] = str(self.html_path)
        dct["debug"] = str(self.debug)
        dct["exit"] = str(self.exit)
        return dct


class Context:
    """
    Stores contextual information for the entire application
    """
    def __init__(self,
                 logger: logging.Logger,
                 web_access_logger: logging.Logger,
                 config: Config,
                 args: Args,
                 status: Status):
        """
        Primary constructor to construct the top-level context
        """
        # Config
        self.logger = logger
        self.web_access_logger = web_access_logger
        self.config = config
        self.args = args
        self.status = status

    def create_child_context(self, context_name: str) -> "Context":
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
        for name, value in self.args.as_dict().items():
            self.logger.debug("  {}: {}".format(name, value))
