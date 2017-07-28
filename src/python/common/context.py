# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging

from .types import Config, Patterns


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