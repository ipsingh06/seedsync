# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from common import overrides, PylftpContext, Persist
from model import IModelListener, ModelFile
from .controller import Controller


class AutoQueuePersist(Persist):
    """
    Persisting state for auto-queue
    """

    # Keys
    __KEY_PATTERNS = "patterns"

    def __init__(self):
        self.patterns = set()

    @classmethod
    @overrides(Persist)
    def from_str(cls: "AutoQueuePersist", content: str) -> "AutoQueuePersist":
        persist = AutoQueuePersist()
        dct = json.loads(content)
        persist.patterns = set(dct[AutoQueuePersist.__KEY_PATTERNS])
        return persist

    @overrides(Persist)
    def to_str(self) -> str:
        dct = dict()
        dct[AutoQueuePersist.__KEY_PATTERNS] = list(self.patterns)
        return json.dumps(dct)


class AutoQueueModelListener(IModelListener):
    def __init__(self):
        self.new_files = []

    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        self.new_files.append(file)

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        pass

    @overrides(IModelListener)
    def file_removed(self, file: ModelFile):
        pass


class AutoQueue:
    """
    Implements auto-queue functionality by sending commands to controller
    as matching files are discovered
    AutoQueue is in the same thread as Controller, so no synchronization is
    needed for now
    """
    def __init__(self,
                 context: PylftpContext,
                 persist: AutoQueuePersist,
                 controller: Controller):
        self.logger = context.logger.getChild("AutoQueue")
        self.__persist = persist
        self.__controller = controller
        self.__model_listener = AutoQueueModelListener()

        initial_model_files = self.__controller.get_model_files_and_add_listener(self.__model_listener)
        # pass the initial model files through to our listener
        for file in initial_model_files:
            self.__model_listener.file_added(file)

        # Print the initial persist state
        self.logger.debug("Auto-Queue Patterns:")
        for pattern in self.__persist.patterns:
            self.logger.debug("    {}".format(pattern))

    def process(self):
        """
        Advance the auto queue state
        :return:
        """
        # Discover any matching new files and queue them
        for file in self.__model_listener.new_files:
            # Files must exist remotely
            if not file.remote_size:
                continue
            # File must be in Default state
            if not file.state == ModelFile.State.DEFAULT:
                continue
            for pattern in self.__persist.patterns:
                if pattern.lower() in file.name.lower():
                    self.logger.info("Auto queueing '{}' for pattern '{}'".format(file.name, pattern))
                    command = Controller.Command(Controller.Command.Action.QUEUE, file.name)
                    self.__controller.queue_command(command)
                    break

        # Clear the processed files
        self.__model_listener.new_files.clear()
