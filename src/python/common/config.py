# Copyright 2017, Inderpreet Singh, All rights reserved.

from configparser import ConfigParser
from typing import Dict
import os

from .error import PylftpError


class PylftpConfig:
    """
    Configuration registry
    """
    class LftpConfig:
        def __init__(self):
            self.address = None
            self.num_max_parallel_downloads = None

    def __init__(self):
        self.lftp = PylftpConfig.LftpConfig()
        self.dict = None  # TODO: remove

    @staticmethod
    def from_file(config_file_path: str) -> "PylftpConfig":
        # Load dict from the file
        if not os.path.isfile(config_file_path):
            raise PylftpError("Config file not found: {}".format(config_file_path))
        config_parser = ConfigParser()
        config_parser.read(config_file_path)
        config_dict = {}
        for section in config_parser.sections():
            config_dict[section] = {}
            for option in config_parser.options(section):
                config_dict[section][option] = config_parser.get(section, option)
        return PylftpConfig.from_dict(config_dict)

    @staticmethod
    def from_dict(config_dict: Dict[str, Dict[str, str]]) -> "PylftpConfig":
        config = PylftpConfig()
        config.dict = config_dict
        return config
