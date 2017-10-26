# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from .error import PylftpError
from .localization import Localization


# Source: https://stackoverflow.com/a/39205612/8571324
T = TypeVar('T', bound='Persist')


class Persist(ABC):
    """
    Defines state that should be persisted between runs
    Provides utility methods to persist/load content to/from file
    Concrete implementations need to implement the from_str() and
    to_str() functionality
    """
    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        if not os.path.isfile(file_path):
            raise PylftpError(Localization.Error.MISSING_FILE.format(file_path))
        with open(file_path, "r") as f:
            return cls.from_str(f.read())

    def to_file(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self.to_str())

    @classmethod
    @abstractmethod
    def from_str(cls: Type[T], content: str) -> T:
        pass

    @abstractmethod
    def to_str(self) -> str:
        pass
