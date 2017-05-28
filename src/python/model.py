# Copyright 2017, Inderpreet Singh, All rights reserved.

import copy
import logging
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

# my libs
from common import PylftpError


class LftpModelError(PylftpError):
    """
    Exception indicating a model error
    """
    pass


class LftpFile:
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
        self.__state = LftpFile.State.DEFAULT  # status
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
        if type(state) != LftpFile.State:
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


class ILftpModelListener(ABC):
    """
    Interface to listen to model events
    """
    @abstractmethod
    def file_added(self, file: LftpFile):
        """
        Event indicating a file was added to the model
        :param file:
        :return:
        """
        pass

    @abstractmethod
    def file_removed(self, file: LftpFile):
        """
        Event indicating that the given file was removed from the model
        :param file:
        :return:
        """
        pass

    @abstractmethod
    def file_updated(self, file: LftpFile):
        """
        Event indicating that the given file was updated
        :param file:
        :return:
        """
        pass


class LftpModel:
    """
    Represents the entire state of lftp
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.__files = {}  # name->LftpFile
        self.__listeners = []

    def add_listener(self, listener: ILftpModelListener):
        """
        Add a model listener
        :param listener:
        :return:
        """
        self.logger.debug("LftpModel: Adding a listener")
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def add_file(self, file: LftpFile):
        """
        Add a file to the model
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Adding file '{}'".format(file.name))
        if file.name in self.__files:
            raise LftpModelError("File already exists in the model")
        self.__files[file.name] = copy.copy(file)
        for listener in self.__listeners:
            listener.file_added(copy.copy(self.__files[file.name]))

    def remove_file(self, file: LftpFile):
        """
        Remove the file from the model
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Removing file '{}'".format(file.name))
        if file.name not in self.__files:
            raise LftpModelError("File does not exist in the model")
        del self.__files[file.name]
        for listener in self.__listeners:
            listener.file_removed(copy.copy(file))

    def update_file(self, file: LftpFile):
        """
        Update an already existing file
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Updating file '{}'".format(file.name))
        if file.name not in self.__files:
            raise LftpModelError("File does not exist in the model")
        self.__files[file.name] = copy.copy(file)
        for listener in self.__listeners:
            listener.file_updated(copy.copy(self.__files[file.name]))

    def get_file(self, name: str) -> LftpFile:
        """
        Returns a copy of the file of the given name
        :param name:
        :return:
        """
        if name not in self.__files:
            raise LftpModelError("File does not exist in the model")
        return copy.copy(self.__files[name])
