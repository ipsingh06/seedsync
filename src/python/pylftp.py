# Copyright 2017, Inderpreet Singh, All rights reserved.

from common import PylftpJob, PylftpContext


class Pylftp(PylftpJob):
    """
    The Pylftp service
    Handles querying and downloading of files
    """
    def __init__(self, context: PylftpContext):
        super().__init__(name=self.__class__.__name__, context=context)
