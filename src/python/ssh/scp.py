# Copyright 2017, Inderpreet Singh, All rights reserved.

import subprocess
import logging
import time

# my libs
from common import PylftpError


class ScpError(PylftpError):
    """
    Custom exception that describes the failure of the ssh command
    """
    pass


class Scp:
    """
    Scp command utility
    """
    def __init__(self, host: str, user: str = None):
        if host is None:
            raise ValueError("Hostname not specified.")
        self.__host = host
        self.__user = user
        self.logger = logging.getLogger("Scp")

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("Scp")

    def copy(self, local_path:str, remote_path:str):
        """
        Copies local file at local_path to remote remote_path
        :param local_path:
        :param remote_path:
        :return:
        """
        if not local_path:
            raise ValueError("Local path cannot be empty")
        if not remote_path:
            raise ValueError("Remote path cannot be empty")
        command_args = [
            "scp",
            "-o", "PasswordAuthentication = no",  # don't ask for password
            local_path
        ]
        if self.__user:
            command_args.append("{}@{}:{}".format(self.__user, self.__host, remote_path))
        else:
            command_args.append("{}:{}".format(self.__host, remote_path))

        self.logger.debug("Command args: {}".format(str(command_args)))
        sp = subprocess.Popen(command_args,
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        start_time = time.time()
        out, err = sp.communicate()
        end_time = time.time()
        self.logger.debug("Return code: {}".format(sp.returncode))
        self.logger.debug("Command took {:.3f}s".format(end_time-start_time))
        if sp.returncode != 0:
            raise ScpError(err.decode())
