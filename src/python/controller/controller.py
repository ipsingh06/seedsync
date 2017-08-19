# Copyright 2017, Inderpreet Singh, All rights reserved.

# my libs
from common import overrides, PylftpJob, PylftpContext


class ControllerJob(PylftpJob):
    """
    The Pylftp service
    Handles querying and downloading of files
    """
    def __init__(self, context: PylftpContext):
        super().__init__(name=self.__class__.__name__, context=context)

    @overrides(PylftpJob)
    def setup(self):
        pass

    @overrides(PylftpJob)
    def execute(self):
        pass

    @overrides(PylftpJob)
    def cleanup(self):
        pass
