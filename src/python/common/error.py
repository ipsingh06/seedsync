# Copyright 2017, Inderpreet Singh, All rights reserved.


class PylftpError(Exception):
    """
    Exception indicating an error
    """
    pass


class ServiceExit(PylftpError):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass
