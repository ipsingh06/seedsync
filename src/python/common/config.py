# Copyright 2017, Inderpreet Singh, All rights reserved.

from configparser import ConfigParser
from typing import Dict
from io import StringIO
import collections

from .error import PylftpError
from .persist import Persist
from .types import overrides


class ConfigError(PylftpError):
    """
    Exception indicating a bad config value
    """
    pass


InnerConfig = Dict[str, str]
OuterConfig = Dict[str, InnerConfig]


def check_section(dct: OuterConfig, name: str) -> InnerConfig:
    if name not in dct:
        raise ConfigError("Missing config section: {}".format(name))
    val = dct[name]
    del dct[name]
    return val


def check_empty_outer_dict(dct: OuterConfig):
    extra_keys = dct.keys()
    if extra_keys:
        raise ConfigError("Unknown section: {}".format(next(iter(extra_keys))))


def check_string(cls, dct: InnerConfig, name: str) -> str:
    if name not in dct:
        raise ConfigError("Missing config: {}.{}".format(cls.__name__, name))
    val = dct[name]
    del dct[name]
    return val


def check_int_positive(cls, dct: InnerConfig, name: str) -> int:
    val_str = check_string_nonempty(cls, dct, name)
    val = int(val_str)
    if val < 0:
        raise ConfigError("Bad config: {}.{} ({}) must be greater than 0".format(
            cls.__name__, name, val
        ))
    return val


def check_string_nonempty(cls, dct: InnerConfig, name: str) -> str:
    val = check_string(cls, dct, name)
    if not val:
        raise ConfigError("Bad config: {}.{} is empty".format(
            cls.__name__, name
        ))
    return val


def check_empty_inner_dict(cls, dct: InnerConfig):
    extra_keys = dct.keys()
    if extra_keys:
        raise ConfigError("Unknown config: {}.{}".format(cls.__name__, next(iter(extra_keys))))


class PylftpConfig(Persist):
    """
    Configuration registry
    """
    class Lftp:
        def __init__(self):
            self.remote_address = None
            self.remote_username = None
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

            config.remote_address = check_string_nonempty(PylftpConfig.Lftp, config_dict, "remote_address")
            config.remote_username = check_string_nonempty(PylftpConfig.Lftp, config_dict, "remote_username")
            config.remote_path = check_string_nonempty(PylftpConfig.Lftp, config_dict, "remote_path")
            config.local_path = check_string_nonempty(PylftpConfig.Lftp, config_dict, "local_path")
            config.remote_path_to_scan_script = check_string_nonempty(
                PylftpConfig.Lftp, config_dict, "remote_path_to_scan_script")

            config.num_max_parallel_downloads = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_parallel_downloads")
            config.num_max_parallel_files_per_download = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_parallel_files_per_download")
            config.num_max_connections_per_file = check_int_positive(
                PylftpConfig.Lftp, config_dict, "num_max_connections_per_file")

            check_empty_inner_dict(PylftpConfig.Lftp, config_dict)
            return config

        def as_dict(self) -> InnerConfig:
            config_dict = collections.OrderedDict()
            config_dict["remote_address"] = self.remote_address
            config_dict["remote_username"] = self.remote_username
            config_dict["remote_path"] = self.remote_path
            config_dict["local_path"] = self.local_path
            config_dict["remote_path_to_scan_script"] = self.remote_path_to_scan_script
            config_dict["num_max_parallel_downloads"] = str(self.num_max_parallel_downloads)
            config_dict["num_max_parallel_files_per_download"] = str(self.num_max_parallel_files_per_download)
            config_dict["num_max_connections_per_file"] = str(self.num_max_connections_per_file)
            return config_dict

    class Controller:
        def __init__(self):
            self.interval_ms_remote_scan = None
            self.interval_ms_local_scan = None
            self.interval_ms_downloading_scan = None

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
            config.interval_ms_downloading_scan = check_int_positive(
                PylftpConfig.Controller, config_dict, "interval_ms_downloading_scan"
            )

            check_empty_inner_dict(PylftpConfig.Controller, config_dict)
            return config

        def as_dict(self) -> InnerConfig:
            config_dict = collections.OrderedDict()
            config_dict["interval_ms_remote_scan"] = str(self.interval_ms_remote_scan)
            config_dict["interval_ms_local_scan"] = str(self.interval_ms_local_scan)
            config_dict["interval_ms_downloading_scan"] = str(self.interval_ms_downloading_scan)
            return config_dict

    class Web:
        def __init__(self):
            self.port = None

        @staticmethod
        def from_dict(config_dict: InnerConfig) -> "PylftpConfig.Web":
            config_dict = dict(config_dict)  # copy that we can modify
            config = PylftpConfig.Web()

            config.port = check_int_positive(
                PylftpConfig.Web, config_dict, "port"
            )

            check_empty_inner_dict(PylftpConfig.Web, config_dict)
            return config

        def as_dict(self) -> InnerConfig:
            config_dict = collections.OrderedDict()
            config_dict["port"] = str(self.port)
            return config_dict

    def __init__(self):
        self.lftp = PylftpConfig.Lftp()
        self.controller = PylftpConfig.Controller()
        self.web = PylftpConfig.Web()

    @classmethod
    @overrides(Persist)
    def from_str(cls: "PylftpConfig", content: str) -> "PylftpConfig":
        config_parser = ConfigParser()
        config_parser.read_string(content)
        config_dict = {}
        for section in config_parser.sections():
            config_dict[section] = {}
            for option in config_parser.options(section):
                config_dict[section][option] = config_parser.get(section, option)
        return PylftpConfig.from_dict(config_dict)

    @overrides(Persist)
    def to_str(self) -> str:
        config_parser = ConfigParser()
        config_dict = self.as_dict()
        for section in config_dict:
            config_parser.add_section(section)
            section_dict = config_dict[section]
            for key in section_dict:
                config_parser.set(section, key, section_dict[key])
        str_io = StringIO()
        config_parser.write(str_io)
        return str_io.getvalue()

    @staticmethod
    def from_dict(config_dict: OuterConfig) -> "PylftpConfig":
        config_dict = dict(config_dict)  # copy that we can modify
        config = PylftpConfig()

        config.lftp = PylftpConfig.Lftp.from_dict(check_section(config_dict, "Lftp"))
        config.controller = PylftpConfig.Controller.from_dict(check_section(config_dict, "Controller"))
        config.web = PylftpConfig.Web.from_dict(check_section(config_dict, "Web"))

        check_empty_outer_dict(config_dict)
        return config

    def as_dict(self) -> OuterConfig:
        # We convert all values back to strings
        # Use an ordered dict to main section order
        config_dict = collections.OrderedDict()
        config_dict["Lftp"] = self.lftp.as_dict()
        config_dict["Controller"] = self.controller.as_dict()
        config_dict["Web"] = self.web.as_dict()
        return config_dict
