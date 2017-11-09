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


class ServiceRestart(PylftpError):
    """
    Exception indicating a restart is requested
    Note: does not extend PylftpError, this is done to differentiate it
          from errors that the top-level module catches and handles
    """
    pass
