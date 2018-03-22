# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import time

import pexpect

# my libs
from common import AppError


class SshcpError(AppError):
    """
    Custom exception that describes the failure of the ssh command
    """
    pass


class Sshcp:
    """
    Scp command utility
    """
    __TIMEOUT_SECS = 180

    def __init__(self,
                 host: str,
                 port: int,
                 user: str = None,
                 password: str = None):
        if host is None:
            raise ValueError("Hostname not specified.")
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild(self.__class__.__name__)

    def __run_command(self,
                      command: str,
                      flags: str,
                      args: str) -> bytes:

        command_args = [
            command,
            flags
        ]

        # Common flags
        command_args += [
            "-o", "StrictHostKeyChecking=no",  # ignore host key changes
            "-o", "UserKnownHostsFile=/dev/null",  # ignore known hosts file
            "-o", "LogLevel=error",  # suppress warnings
        ]

        if self.__password is None:
            command_args += [
                "-o", "PasswordAuthentication=no",  # don't ask for password
            ]
        else:
            command_args += [
                "-o", "PubkeyAuthentication=no"  # don't use key authentication
            ]

        command_args.append(args)

        command = " ".join(command_args)
        self.logger.debug("Command: {}".format(command))

        start_time = time.time()
        sp = pexpect.spawn(command)
        try:
            if self.__password is not None:
                i = sp.expect([
                    'password: ',  # i=0, all's good
                    'lost connection',  # i=1, bad hostname
                    'Could not resolve hostname',  # i=2, bad hostname
                ])
                if i in (1, 2):
                    raise SshcpError("Bad hostname: {}".format(self.__host))
                sp.sendline(self.__password)

            i = sp.expect(
                [
                    pexpect.EOF,  # i=0, all's good
                    'password: ',  # i=1, wrong password
                    'lost connection',  # i=2, bad hostname
                    'Could not resolve hostname',  # i=3, bad hostname
                ],
                timeout=self.__TIMEOUT_SECS
            )
            if i == 1:
                raise SshcpError("Incorrect password")
            elif i in (2, 3):
                raise SshcpError("Bad hostname: {}".format(self.__host))

        except pexpect.exceptions.TIMEOUT:
            self.logger.exception("Timed out")
            self.logger.error("Command output before:\n{}".format(sp.before))
            raise SshcpError("Timed out")
        sp.close()
        end_time = time.time()

        self.logger.debug("Return code: {}".format(sp.exitstatus))
        self.logger.debug("Command took {:.3f}s".format(end_time-start_time))
        if sp.exitstatus != 0:
            raise SshcpError(sp.before.decode())

        return sp.before.replace(b'\r\n', b'\n').strip()

    def shell(self, command: str) -> bytes:
        """
        Run a shell command on remote service and return output
        :param command:
        :return:
        """
        if not command:
            raise ValueError("Command cannot be empty")

        # escape the command
        if "'" in command and '"' in command:
            # I don't know how to handle this yet...
            raise ValueError("Command cannot contain both single and double quotes")
        elif '"' in command:
            # double quote in command, cover with single quotes
            command = "'{}'".format(command)
        else:
            # no double quote in command, cover with double quotes
            command = '"{}"'.format(command)

        flags = [
            "-p", str(self.__port),  # port
        ]
        args = [
            "{}@{}".format(self.__user, self.__host),
            command
        ]
        return self.__run_command(
            command="ssh",
            flags=" ".join(flags),
            args=" ".join(args)
        )

    def copy(self, local_path: str, remote_path: str):
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

        flags = [
            "-q",  # quiet
            "-P", str(self.__port),  # port
        ]
        args = [
            local_path,
            "{}@{}:{}".format(self.__user, self.__host, remote_path)
        ]
        self.__run_command(
            command="scp",
            flags=" ".join(flags),
            args=" ".join(args)
        )
