# Copyright 2017, Inderpreet Singh, All rights reserved.

from configparser import ConfigParser
from typing import Dict
import os

from .error import PylftpError


InnerConfig = Dict[str, str]
OuterConfig = Dict[str, InnerConfig]


def check_section(dct: OuterConfig, name: str) -> InnerConfig:
    if name not in dct:
        raise PylftpError("Missing config section: {}".format(name))
    val = dct[name]
    del dct[name]
    return val


def check_empty_outer_dict(dct: OuterConfig):
    extra_keys = dct.keys()
    if extra_keys:
        raise PylftpError("Unknown section: {}".format(next(iter(extra_keys))))


def check_string(cls, dct: InnerConfig, name: str) -> str:
    if name not in dct:
        raise PylftpError("Missing config: {}.{}".format(cls.__name__, name))
    val = dct[name]
    del dct[name]
    return val


def check_int_positive(cls, dct: InnerConfig, name: str) -> int:
    val_str = check_string(cls, dct, name)
    val = int(val_str)
    if val < 0:
        raise PylftpError("Bad config: {}.{} ({}) must be greater than 0".format(
            cls.__name__, name, val
        ))
    return val


def check_empty_inner_dict(cls, dct: InnerConfig):
    extra_keys = dct.keys()
    if extra_keys:
        raise PylftpError("Unknown config: {}.{}".format(cls.__name__, next(iter(extra_keys))))


class PylftpConfig:
    """
    Configuration registry
    """
    class Lftp:
        def __init__(self):
            self.remote_address = None
            self.remote_username = None
            self.remote_password = None
            self.remote_path = None
            self.local_path = None
            self.remote_path_to_scan_script = None
            self.num_max_parallel_downloads = None
            self.num_max_parallel_files_per_download = None
            self.num_max_connections_per_file = None

        @staticmethod
        def from_dict(config_dict: InnerConfig) -> "PylftpConfig.Lftp":
            config_dict = dict(config_dict)  # copy that we can modify
            config = PylftpConfig.Lftp()

            config.remote_address = check_string(PylftpConfig.Lftp, config_dict, "remote_address")
            config.remote_username = check_string(PylftpConfig.Lftp, config_dict, "remote_username")
            config.remote_password = check_string(PylftpConfig.Lftp, config_dict, "remote_password")
            config.remote_path = check_string(PylftpConfig.Lftp, config_dict, "remote_path")
            config.local_path = check_string(PylftpConfig.Lftp, config_dict, "local_path")
            config.remote_path_to_scan_script = check_string(
                PylftpConfig.Lftp, config_dict, "remote_path_to_scan_script")

            config.num_max_parallel_downloads = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_parallel_downloads")
            config.num_max_parallel_files_per_download = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_parallel_files_per_download")
            config.num_max_connections_per_file = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_connections_per_file")

            check_empty_inner_dict(PylftpConfig.Lftp, config_dict)
            return config

    class Controller:
        def __init__(self):
            self.interval_ms_remote_scan = None
            self.interval_ms_local_scan = None

        @staticmethod
        def from_dict(config_dict: InnerConfig) -> "PylftpConfig.Controller":
            config_dict = dict(config_dict)  # copy that we can modify
            config = PylftpConfig.Controller()

            config.interval_ms_remote_scan = check_int_positive(
                PylftpConfig.Controller, config_dict, "interval_ms_remote_scan"
            )
            config.interval_ms_local_scan = check_int_positive(
                PylftpConfig.Controller, config_dict, "interval_ms_local_scan"
            )

            check_empty_inner_dict(PylftpConfig.Controller, config_dict)
            return config

    def __init__(self):
        self.lftp = PylftpConfig.Lftp()
        self.controller = PylftpConfig.Controller()

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
    def from_dict(config_dict: OuterConfig) -> "PylftpConfig":
        config_dict = dict(config_dict)  # copy that we can modify
        config = PylftpConfig()

        config.lftp = PylftpConfig.Lftp.from_dict(check_section(config_dict, "Lftp"))
        config.controller = PylftpConfig.Controller.from_dict(check_section(config_dict, "Controller"))

        check_empty_outer_dict(config_dict)
        return config

    def as_dict(self) -> OuterConfig:
        # We convert all values back to strings
        config_dict = dict()
        config_dict["Lftp"] = {k: str(v) for k, v in self.lftp.__dict__.items()}
        config_dict["Controller"] = {k: str(v) for k, v in self.controller.__dict__.items()}
        return config_dict
