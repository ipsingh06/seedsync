# Copyright 2017, Inderpreet Singh, All rights reserved.

from datetime import datetime
from enum import Enum


class ModelFile:
    """
    Represents a file or directory
    """
    class State(Enum):
        DEFAULT = 0
        DOWNLOADING = 1
        DOWNLOADED = 2
        QUEUED = 3
        DELETED_LOCALLY = 4  # exists remotely
        DELETED_REMOTELY = 5  # exists locally

    def __init__(self, name: str):
        self.__name = name  # file or folder name
        self.__state = ModelFile.State.DEFAULT  # status
        self.__remote_size = None  # remote size in bytes
        self.__local_size = None  # local size in bytes
        self.__downloading_speed = None  # in bytes / sec
        self.__update_timestamp = None  # timestamp of the latest update

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    @property
    def name(self) -> str: return self.__name

    @property
    def state(self) -> State: return self.__state

    @state.setter
    def state(self, state: State):
        if type(state) != ModelFile.State:
            raise TypeError
        self.__state = state

    @property
    def remote_size(self) -> int: return self.__remote_size

    @remote_size.setter
    def remote_size(self, remote_size: int):
        if type(remote_size) != int:
            raise TypeError
        if remote_size < 0:
            raise ValueError
        self.__remote_size = remote_size

    @property
    def local_size(self) -> int: return self.__local_size

    @local_size.setter
    def local_size(self, local_size: int):
        if type(local_size) != int:
            raise TypeError
        if local_size < 0:
            raise ValueError
        self.__local_size = local_size

    @property
    def downloading_speed(self) -> int: return self.__downloading_speed

    @downloading_speed.setter
    def downloading_speed(self, downloading_speed: int):
        if type(downloading_speed) != int:
            raise TypeError
        if downloading_speed < 0:
            raise ValueError
        self.__downloading_speed = downloading_speed

    @property
    def update_timestamp(self) -> datetime: return self.__update_timestamp

    @update_timestamp.setter
    def update_timestamp(self, update_timestamp: datetime):
        if type(update_timestamp) != datetime:
            raise TypeError
        self.__update_timestamp = update_timestamp