# Copyright 2017, Inderpreet Singh, All rights reserved.

import copy
import logging
from abc import ABC, abstractmethod

# my libs
from common import PylftpError
from .file import ModelFile


class ModelError(PylftpError):
    """
    Exception indicating a model error
    """
    pass


class IModelListener(ABC):
    """
    Interface to listen to model events
    """
    @abstractmethod
    def file_added(self, file: ModelFile):
        """
        Event indicating a file was added to the model
        :param file:
        :return:
        """
        pass

    @abstractmethod
    def file_removed(self, file: ModelFile):
        """
        Event indicating that the given file was removed from the model
        :param file:
        :return:
        """
        pass

    @abstractmethod
    def file_updated(self, file: ModelFile):
        """
        Event indicating that the given file was updated
        :param file:
        :return:
        """
        pass


class Model:
    """
    Represents the entire state of lftp
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.__files = {}  # name->LftpFile
        self.__listeners = []

    def add_listener(self, listener: IModelListener):
        """
        Add a model listener
        :param listener:
        :return:
        """
        self.logger.debug("LftpModel: Adding a listener")
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def add_file(self, file: ModelFile):
        """
        Add a file to the model
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Adding file '{}'".format(file.name))
        if file.name in self.__files:
            raise ModelError("File already exists in the model")
        self.__files[file.name] = copy.copy(file)
        for listener in self.__listeners:
            listener.file_added(copy.copy(self.__files[file.name]))

    def remove_file(self, file: ModelFile):
        """
        Remove the file from the model
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Removing file '{}'".format(file.name))
        if file.name not in self.__files:
            raise ModelError("File does not exist in the model")
        del self.__files[file.name]
        for listener in self.__listeners:
            listener.file_removed(copy.copy(file))

    def update_file(self, file: ModelFile):
        """
        Update an already existing file
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Updating file '{}'".format(file.name))
        if file.name not in self.__files:
            raise ModelError("File does not exist in the model")
        self.__files[file.name] = copy.copy(file)
        for listener in self.__listeners:
            listener.file_updated(copy.copy(self.__files[file.name]))

    def get_file(self, name: str) -> ModelFile:
        """
        Returns a copy of the file of the given name
        :param name:
        :return:
        """
        if name not in self.__files:
            raise ModelError("File does not exist in the model")
        return copy.copy(self.__files[name])
