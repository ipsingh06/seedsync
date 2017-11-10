# Copyright 2017, Inderpreet Singh, All rights reserved.

from configparser import ConfigParser
from typing import Dict
from io import StringIO
import collections
from distutils.util import strtobool
from abc import ABC
from typing import Type, TypeVar, Callable

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


# Source: https://stackoverflow.com/a/39205612/8571324
T = TypeVar('T', bound='PylftpInnerConfig')


class PylftpInnerConfig(ABC):
    """
    Abstract base class for an config section
    Provides utility methods for checking and parsing string values to proper types
    """
    def __init__(self):
        self.__registry = collections.OrderedDict()  # registry of values, maps name -> checker method

    def _register_value(self, name, checker_method: Callable):
        self.__registry[name] = checker_method
        return "Unset"

    @classmethod
    def from_dict(cls: Type[T], config_dict: InnerConfig) -> T:
        """
        Construct and return inner config from a dict
        :param config_dict:
        :return:
        """
        config_dict = dict(config_dict)  # copy that we can modify

        # noinspection PyCallingNonCallable
        inner_config = cls()
        for name, checker_method in inner_config.__registry.items():
            setattr(inner_config, name, checker_method(config_dict, name))

        PylftpInnerConfig._check_empty_inner_dict(config_dict)

        return inner_config

    def as_dict(self) -> InnerConfig:
        """
        Return the dict representation of the inner config
        :return:
        """
        config_dict = collections.OrderedDict()
        for name, _ in self.__registry.items():
            config_dict[name] = str(getattr(self, name))
        return config_dict

    @classmethod
    def _check_empty_inner_dict(cls, dct: InnerConfig):
        extra_keys = dct.keys()
        if extra_keys:
            raise ConfigError("Unknown config: {}.{}".format(cls.__name__, next(iter(extra_keys))))

    @classmethod
    def _check_bool(cls, dct: InnerConfig, name: str) -> bool:
        val_str = cls._check_string_nonempty(dct, name)
        try:
            val = bool(strtobool(val_str))
        except ValueError:
            raise ConfigError("Bad config: {}.{} ({}) must be a boolean value".format(
                cls.__name__, name, val_str
            ))
        return val

    @classmethod
    def _check_int_positive(cls, dct: InnerConfig, name: str) -> int:
        val_str = cls._check_string_nonempty(dct, name)
        val = int(val_str)
        if val < 1:
            raise ConfigError("Bad config: {}.{} ({}) must be greater than 0".format(
                cls.__name__, name, val
            ))
        return val

    @classmethod
    def _check_int_non_negative(cls, dct: InnerConfig, name: str) -> int:
        val_str = cls._check_string_nonempty(dct, name)
        val = int(val_str)
        if val < 0:
            raise ConfigError("Bad config: {}.{} ({}) must be zero or greater".format(
                cls.__name__, name, val
            ))
        return val

    @classmethod
    def _check_string_nonempty(cls, dct: InnerConfig, name: str) -> str:
        val = cls._check_string(dct, name)
        if not val:
            raise ConfigError("Bad config: {}.{} is empty".format(
                cls.__name__, name
            ))
        return val

    @classmethod
    def _check_string(cls, dct: InnerConfig, name: str) -> str:
        if name not in dct:
            raise ConfigError("Missing config: {}.{}".format(cls.__name__, name))
        val = dct[name]
        del dct[name]
        return val


class PylftpConfig(Persist):
    """
    Configuration registry
    """
    class General(PylftpInnerConfig):
        def __init__(self):
            super().__init__()
            self.debug = self._register_value("debug", self._check_bool)

    class Lftp(PylftpInnerConfig):
        def __init__(self):
            super().__init__()
            self.remote_address = self._register_value("remote_address", self._check_string_nonempty)
            self.remote_username = self._register_value("remote_username", self._check_string_nonempty)
            self.remote_path = self._register_value("remote_path", self._check_string_nonempty)
            self.local_path = self._register_value("local_path", self._check_string_nonempty)
            self.remote_path_to_scan_script = self._register_value("remote_path_to_scan_script",
                                                                   self._check_string_nonempty)
            self.num_max_parallel_downloads = self._register_value("num_max_parallel_downloads",
                                                                   self._check_int_positive)
            self.num_max_parallel_files_per_download = self._register_value("num_max_parallel_files_per_download",
                                                                            self._check_int_positive)
            self.num_max_connections_per_root_file = self._register_value("num_max_connections_per_root_file",
                                                                          self._check_int_positive)
            self.num_max_connections_per_dir_file = self._register_value("num_max_connections_per_dir_file",
                                                                         self._check_int_positive)
            self.num_max_total_connections = self._register_value("num_max_total_connections",
                                                                  self._check_int_non_negative)

    class Controller(PylftpInnerConfig):
        def __init__(self):
            super().__init__()
            self.interval_ms_remote_scan = self._register_value("interval_ms_remote_scan",
                                                                self._check_int_positive)
            self.interval_ms_local_scan = self._register_value("interval_ms_local_scan",
                                                               self._check_int_positive)
            self.interval_ms_downloading_scan = self._register_value("interval_ms_downloading_scan",
                                                                     self._check_int_positive)

    class Web(PylftpInnerConfig):
        def __init__(self):
            super().__init__()
            self.port = self._register_value("port", self._check_int_positive)

    def __init__(self):
        self.general = PylftpConfig.General()
        self.lftp = PylftpConfig.Lftp()
        self.controller = PylftpConfig.Controller()
        self.web = PylftpConfig.Web()

    @staticmethod
    def _check_section(dct: OuterConfig, name: str) -> InnerConfig:
        if name not in dct:
            raise ConfigError("Missing config section: {}".format(name))
        val = dct[name]
        del dct[name]
        return val

    @staticmethod
    def _check_empty_outer_dict(dct: OuterConfig):
        extra_keys = dct.keys()
        if extra_keys:
            raise ConfigError("Unknown section: {}".format(next(iter(extra_keys))))

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

        config.general = PylftpConfig.General.from_dict(PylftpConfig._check_section(config_dict, "General"))
        config.lftp = PylftpConfig.Lftp.from_dict(PylftpConfig._check_section(config_dict, "Lftp"))
        config.controller = PylftpConfig.Controller.from_dict(PylftpConfig._check_section(config_dict, "Controller"))
        config.web = PylftpConfig.Web.from_dict(PylftpConfig._check_section(config_dict, "Web"))

        PylftpConfig._check_empty_outer_dict(config_dict)
        return config

    def as_dict(self) -> OuterConfig:
        # We convert all values back to strings
        # Use an ordered dict to main section order
        config_dict = collections.OrderedDict()
        config_dict["General"] = self.general.as_dict()
        config_dict["Lftp"] = self.lftp.as_dict()
        config_dict["Controller"] = self.controller.as_dict()
        config_dict["Web"] = self.web.as_dict()
        return config_dict
