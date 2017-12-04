# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from .error import PylftpError
from .localization import Localization


# Source: https://stackoverflow.com/a/39205612/8571324
T_Persist = TypeVar('T_Persist', bound='Persist')
T_Serializable = TypeVar('T_Serializable', bound='Serializable')


class Serializable(ABC):
    """
    Defines a class that is serializable to string.
    The string representation must be human readable (i.e. not pickle)
    """
    @classmethod
    @abstractmethod
    def from_str(cls: Type[T_Serializable], content: str) -> T_Serializable:
        pass

    @abstractmethod
    def to_str(self) -> str:
        pass


class PersistError(PylftpError):
    """
    Exception indicating persist loading/saving error
    """
    pass


class Persist(Serializable):
    """
    Defines state that should be persisted between runs
    Provides utility methods to persist/load content to/from file
    Concrete implementations need to implement the from_str() and
    to_str() functionality
    """
    @classmethod
    def from_file(cls: Type[T_Persist], file_path: str) -> T_Persist:
        if not os.path.isfile(file_path):
            raise PylftpError(Localization.Error.MISSING_FILE.format(file_path))
        with open(file_path, "r") as f:
            return cls.from_str(f.read())

    def to_file(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self.to_str())

    @classmethod
    @abstractmethod
    def from_str(cls: Type[T_Persist], content: str) -> T_Persist:
        pass

    @abstractmethod
    def to_str(self) -> str:
        pass
