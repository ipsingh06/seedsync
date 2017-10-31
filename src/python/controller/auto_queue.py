# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from common import overrides, Constants, PylftpContext, Persist
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
        return json.dumps(dct, indent=Constants.JSON_PRETTY_PRINT_INDENT)


class AutoQueueModelListener(IModelListener):
    def __init__(self):
        self.new_files = []  # list of new files
        self.modified_files = []  # list of pairs (old_file, new_file)

    @overrides(IModelListener)
    def file_added(self, file: ModelFile):
        self.new_files.append(file)

    @overrides(IModelListener)
    def file_updated(self, old_file: ModelFile, new_file: ModelFile):
        self.modified_files.append((old_file, new_file))

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
        # Build a list of candidate file
        candidate_file = []

        # Accept new files that exist remotely
        for file in self.__model_listener.new_files:
            # Files must exist remotely
            if not file.remote_size:
                continue
            # File must be in Default state
            if not file.state == ModelFile.State.DEFAULT:
                continue
            candidate_file.append(file)

        # Accept modified files that were just discovered on remote
        for old_file, new_file in self.__model_listener.modified_files:
            # Files must exist remotely
            if not new_file.remote_size:
                continue
            # File was just discovered
            if old_file.remote_size is not None:
                continue
            # File must be in Default state
            if not new_file.state == ModelFile.State.DEFAULT:
                continue
            candidate_file.append(new_file)

        # Filter candidate files with those matching a pattern
        for file in candidate_file:
            for pattern in self.__persist.patterns:
                if pattern.lower() in file.name.lower():
                    self.logger.info("Auto queueing '{}' for pattern '{}'".format(file.name, pattern))
                    command = Controller.Command(Controller.Command.Action.QUEUE, file.name)
                    self.__controller.queue_command(command)
                    break

        # Clear the processed files
        self.__model_listener.new_files.clear()
        self.__model_listener.modified_files.clear()
