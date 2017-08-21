# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from abc import ABC, abstractmethod
from typing import Set

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
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        """
        Event indicating that the given file was updated
        :param old_file:
        :param new_file:
        :return:
        """
        pass


class Model:
    """
    Represents the entire state of lftp
    """
    def __init__(self):
        self.logger = logging.getLogger("Model")
        self.__files = {}  # name->LftpFile
        self.__listeners = []

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("Model")

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
        self.__files[file.name] = file
        for listener in self.__listeners:
            listener.file_added(self.__files[file.name])

    def remove_file(self, filename: str):
        """
        Remove the file from the model
        :param filename:
        :return:
        """
        self.logger.debug("LftpModel: Removing file '{}'".format(filename))
        if filename not in self.__files:
            raise ModelError("File does not exist in the model")
        file = self.__files[filename]
        del self.__files[filename]
        for listener in self.__listeners:
            listener.file_removed(file)

    def update_file(self, file: ModelFile):
        """
        Update an already existing file
        :param file:
        :return:
        """
        self.logger.debug("LftpModel: Updating file '{}'".format(file.name))
        if file.name not in self.__files:
            raise ModelError("File does not exist in the model")
        old_file = self.__files[file.name]
        new_file = file
        self.__files[file.name] = new_file
        for listener in self.__listeners:
            listener.file_updated(old_file, new_file)

    def get_file(self, name: str) -> ModelFile:
        """
        Returns a copy of the file of the given name
        :param name:
        :return:
        """
        if name not in self.__files:
            raise ModelError("File does not exist in the model")
        return self.__files[name]

    def get_file_names(self) -> Set[str]:
        return set(self.__files.keys())
