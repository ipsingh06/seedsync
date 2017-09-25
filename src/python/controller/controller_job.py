# Copyright 2017, Inderpreet Singh, All rights reserved.


# my libs
from common import overrides, PylftpJob, PylftpContext
from .controller import Controller


class ControllerJob(PylftpJob):
    """
    The Pylftp service
    Handles querying and downloading of files
    """
    def __init__(self, context: PylftpContext, controller: "Controller"):
        super().__init__(name=self.__class__.__name__, context=context)
        self.__context = context
        self.__controller = controller

    @overrides(PylftpJob)
    def setup(self):
        pass

    @overrides(PylftpJob)
    def execute(self):
        self.__controller.process()

    @overrides(PylftpJob)
    def cleanup(self):
        pass