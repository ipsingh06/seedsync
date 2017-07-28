# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import List


class SystemFile:
    """
    Represents a system file or directory
    """
    def __init__(self, name: str, size: int, is_dir: bool = False):
        if size < 0:
            raise ValueError("File size must be greater than zero")
        self.__name = name
        self.__size = size  # in bytes
        self.__is_dir = is_dir
        self.__children = []

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    @property
    def name(self) -> str: return self.__name

    @property
    def size(self) -> int: return self.__size

    @property
    def is_dir(self) -> bool: return self.__is_dir

    @property
    def children(self) -> List["SystemFile"]: return self.__children

    def add_child(self, file: "SystemFile"):
        if not self.__is_dir:
            raise TypeError("Cannot add children to a file")
        self.__children.append(file)