# Copyright 2017, Inderpreet Singh, All rights reserved.

import subprocess
import logging
import time

# my libs
from common import AppError


class SshError(AppError):
    """
    Custom exception that describes the failure of the ssh command
    """
    pass


class Ssh:
    """
    SSH command utility
    """
    def __init__(self,
                 host: str,
                 port: int,
                 user: str = None,
                 target_dir: str = None):
        if host is None:
            raise ValueError("Hostname not specified.")
        self.__host = host
        self.__port = port
        self.__user = user
        self.__target_dir = target_dir
        self.logger = logging.getLogger("Ssh")

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("Ssh")

    def run_command(self, command: str) -> bytes:
        """
        Returns the output of the remote command as a bytes
        :param command:
        :return:
        """
        if not command:
            raise ValueError("Command cannot be empty")
        command_args = [
            "ssh",
            "-o", "PasswordAuthentication = no",  # don't ask for password
            "-p", str(self.__port)
        ]
        if self.__user:
            command_args.append("{}@{}".format(self.__user, self.__host))
        else:
            command_args.append("{}".format(self.__host))
        if self.__target_dir:
            command_args.append("cd {}; {}".format(self.__target_dir, command))
        else:
            command_args.append("{}".format(command))

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
            raise SshError(err.decode())
        return out
