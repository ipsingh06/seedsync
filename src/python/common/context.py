# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import os
import sys
import copy
import argparse
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler

# my libs
from .types import Config, Patterns
from .error import PylftpError
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
        self.args = self.__parse_args()

        # Logger setup
        # We separate the main log from the web-access log
        self.logger = self.__create_logger(name=Constants.SERVICE_NAME,
                                           debug=self.args.debug,
                                           logdir=self.args.logdir)
        self.web_access_logger = self.__create_logger(name=Constants.WEB_ACCESS_LOG_NAME,
                                                      debug=self.args.debug,
                                                      logdir=self.args.logdir)

        # Config
        self.config = PylftpContext.__load_config(self.args.config)

        # Patterns
        self.patterns = PylftpContext.__load_patterns(self.args.patterns)

    def create_child_context(self, context_name: str) -> "PylftpContext":
        child_context = copy.copy(self)
        child_context.logger = self.logger.getChild(context_name)
        return child_context

    @staticmethod
    def __parse_args():
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("-c", "--config", required=True, help="Path to config file")
        parser.add_argument("-p", "--patterns", required=True, help="Path to patterns file")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")
        return parser.parse_args()

    @staticmethod
    def __create_logger(name: str, debug: bool, logdir: str) -> logging.Logger:
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

    @staticmethod
    def __load_config(config_file_path: str) -> Config:
        if not os.path.isfile(config_file_path):
            raise PylftpError("Config file not found: {}".format(config_file_path))
        config_parser = ConfigParser()
        config_parser.read(config_file_path)
        config = {}
        for section in config_parser.sections():
            config[section] = {}
            for option in config_parser.options(section):
                config[section][option] = config_parser.get(section, option)
        return config

    @staticmethod
    def __load_patterns(patterns_file_path: str) -> Patterns:
        if not os.path.isfile(patterns_file_path):
            raise PylftpError("Patterns file not found: {}".format(patterns_file_path))
        with open(patterns_file_path) as f:
            patterns = [x.strip() for x in f.readlines()]
        return patterns

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
