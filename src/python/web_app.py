# Copyright 2017, Inderpreet Singh, All rights reserved.

from common import PylftpJob, PylftpContext


class WebApp(PylftpJob):
    """
    Web interface service 
    :return: 
    """
    def __init__(self, context: PylftpContext):
        super().__init__(name=self.__class__.__name__, context=context)
