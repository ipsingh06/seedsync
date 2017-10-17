# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import re
from functools import wraps
from typing import Callable, Union, List

# 3rd party libs
import pexpect

# my libs
from common import PylftpError
from .job_status_parser import LftpJobStatus, LftpJobStatusParser


class LftpError(PylftpError):
    """
    Custom exception that describes the failure of the lftp command
    """
    pass


class Lftp:
    """
    Lftp command utility
    """
    __SET_NUM_PARALLEL_FILES = "mirror:parallel-transfer-count"
    __SET_NUM_CONNECTIONS_PGET = "pget:default-n"
    __SET_NUM_CONNECTIONS_MIRROR = "mirror:use-pget-n"
    __SET_NUM_MAX_TOTAL_CONNECTIONS = "net:connection-limit"
    __SET_RATE_LIMIT = "net:limit-rate"
    __SET_MIN_CHUNK_SIZE = "pget:min-chunk-size"
    __SET_NUM_PARALLEL_JOBS = "cmd:queue-parallel"
    __SET_MOVE_BACKGROUND_ON_EXIT = "cmd:move-background"
    __SET_COMMAND_AT_EXIT = "cmd:at-exit"

    # Set this to True to enable verbose command logging
    __LOG_COMMAND_OUTPUT = False

    def __init__(self, address: str, user: str, password: str):
        self.__user = user
        self.__password = password
        self.__address = address
        self.__base_remote_dir_path = ""
        self.__base_local_dir_path = ""
        self.logger = logging.getLogger("Lftp")
        self.__expect_pattern = "lftp {}@{}:.*>".format(self.__user, self.__address)
        self.__job_status_parser = LftpJobStatusParser()

        args = [
            "-u", "{},{}".format(self.__user, self.__password),
            "sftp://{}".format(self.__address)
        ]
        self.__process = pexpect.spawn("/usr/bin/lftp", args)
        self.__process.expect(self.__expect_pattern)
        self.__setup()

    def __setup(self):
        """
        Setup the lftp instance with default settings
        :return:
        """
        # Set to kill on exit to prevent a zombie process
        self.__set(Lftp.__SET_COMMAND_AT_EXIT, "\"kill all\"")

    def with_check_process(method: Callable):
        """
        Decorator that checks for a valid process before executing
        the decorated method
        :param method:
        :return:
        """
        @wraps(method)
        def wrapper(inst: "Lftp", *args, **kwargs):
            if inst.__process is None or not inst.__process.isalive():
                raise LftpError("lftp process is not running")
            return method(inst, *args, **kwargs)
        return wrapper

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("Lftp")
        self.__job_status_parser.set_base_logger(self.logger)

    def set_base_remote_dir_path(self, base_remote_dir_path: str):
        self.__base_remote_dir_path = base_remote_dir_path

    def set_base_local_dir_path(self, base_local_dir_path: str):
        self.__base_local_dir_path = base_local_dir_path

    @with_check_process
    def __run_command(self, command: str):
        if Lftp.__LOG_COMMAND_OUTPUT:
            self.logger.debug("command: {}".format(command))
        self.__process.sendline(command)
        self.__process.expect(self.__expect_pattern)
        out = self.__process.before.decode()
        out = out.strip()  # remove any CRs

        if Lftp.__LOG_COMMAND_OUTPUT:
            self.logger.debug("out:")
            for line in out.split("\n"):
                self.logger.debug("  {}".format(line))

        # let's try and detect some errors
        if self.__detect_errors_from_output(out):
            # we need to consume the actual output so that
            # it doesn't get passed onto next command
            error_out = out
            self.__process.expect(self.__expect_pattern)
            out = self.__process.before.decode()
            out = out.strip()  # remove any CRs
            if Lftp.__LOG_COMMAND_OUTPUT:
                self.logger.debug("retry out:")
                for line in out.split("\n"):
                    self.logger.debug("  {}".format(line))
            raise LftpError("Detected error: {}".format(error_out))
        return out

    @staticmethod
    def __detect_errors_from_output(out: str) -> bool:
        errors_m = [
            re.compile("^(?:pget|mirror): Access failed: .*$")
        ]
        for m in errors_m:
            if m.match(out):
                return True
        return False

    def __set(self, setting: str, value: str):
        """
        Set a setting in the lftp runtime
        :param setting:
        :param value:
        :return:
        """
        self.__run_command("set {} {}".format(setting, value))

    def __get(self, setting: str) -> str:
        """
        Get a setting from the lftp runtime
        :param setting:
        :return:
        """
        out = self.__run_command("set -a | grep {}".format(setting))
        m = re.search("set {} (.*)".format(setting), out)
        if not m or not m.group or not m.group(1):
            raise LftpError("Failed to get setting '{}'. Output: '{}'".format(setting, out))
        return m.group(1).strip()

    @staticmethod
    def __to_bool(value: str) -> bool:
        # sets are taken from LFTP manual
        if value.lower() in {"true", "on", "yes", "1", "+"}:
            return True
        elif value.lower() in {"false",  "off", "no", "0", "-"}:
            return False
        else:
            raise LftpError("Cannot convert value '{}' to boolean".format(value))

    @property
    def num_connections_per_dir_file(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_CONNECTIONS_MIRROR))

    @num_connections_per_dir_file.setter
    def num_connections_per_dir_file(self, num_connections: int):
        if num_connections < 1:
            raise ValueError("Number of connections must be positive")
        self.__set(Lftp.__SET_NUM_CONNECTIONS_MIRROR, str(num_connections))

    @property
    def num_connections_per_root_file(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_CONNECTIONS_PGET))

    @num_connections_per_root_file.setter
    def num_connections_per_root_file(self, num_connections: int):
        if num_connections < 1:
            raise ValueError("Number of connections must be positive")
        self.__set(Lftp.__SET_NUM_CONNECTIONS_PGET, str(num_connections))

    @property
    def num_max_total_connections(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_MAX_TOTAL_CONNECTIONS))

    @num_max_total_connections.setter
    def num_max_total_connections(self, num_connections: int):
        if num_connections < 0:
            raise ValueError("Number of connections must be zero or greater")
        self.__set(Lftp.__SET_NUM_MAX_TOTAL_CONNECTIONS, str(num_connections))

    @property
    def num_parallel_files(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_PARALLEL_FILES))

    @num_parallel_files.setter
    def num_parallel_files(self, num_parallel_files: int):
        if num_parallel_files < 1:
            raise ValueError("Number of parallel files must be positive")
        self.__set(Lftp.__SET_NUM_PARALLEL_FILES, str(num_parallel_files))

    @property
    def rate_limit(self) -> str:
        return self.__get(Lftp.__SET_RATE_LIMIT)

    @rate_limit.setter
    def rate_limit(self, rate_limit: Union[int, str]):
        self.__set(Lftp.__SET_RATE_LIMIT, str(rate_limit))

    @property
    def min_chunk_size(self) -> str:
        return self.__get(Lftp.__SET_MIN_CHUNK_SIZE)

    @min_chunk_size.setter
    def min_chunk_size(self, min_chunk_size: Union[int, str]):
        self.__set(Lftp.__SET_MIN_CHUNK_SIZE, str(min_chunk_size))

    @property
    def num_parallel_jobs(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_PARALLEL_JOBS))

    @num_parallel_jobs.setter
    def num_parallel_jobs(self, num_parallel_jobs: int):
        if num_parallel_jobs < 1:
            raise ValueError("Number of parallel jobs must be positive")
        self.__set(Lftp.__SET_NUM_PARALLEL_JOBS, str(num_parallel_jobs))

    @property
    def move_background_on_exit(self) -> bool:
        return Lftp.__to_bool(self.__get(Lftp.__SET_MOVE_BACKGROUND_ON_EXIT))

    @move_background_on_exit.setter
    def move_background_on_exit(self, move_background_on_exit: bool):
        self.__set(Lftp.__SET_MOVE_BACKGROUND_ON_EXIT, str(int(move_background_on_exit)))

    def status(self) -> List[LftpJobStatus]:
        """
        Return a status list of queued and running jobs
        :return:
        """
        out = self.__run_command("jobs -v")
        # remove the command from output, if it exists
        statuses_str = re.sub("^\s*jobs -v\s*$", "", out, flags=re.MULTILINE)
        statuses = self.__job_status_parser.parse(statuses_str)
        return statuses

    def queue(self, name: str, is_dir: bool):
        """
        Queues a job for download
        This method may cause an exception to be generated in a later method call:
          * Wrong type (is_dir) is specified
          * File/folder does not exist
        :param name: name of file or folder to download
        :param is_dir: true if folder, false if file
        :return:
        """
        command = " ".join([
            "queue",
            "'",
            "pget" if not is_dir else "mirror",
            "-c",
            "\"{remote_dir}/{filename}\"".format(remote_dir=self.__base_remote_dir_path,
                                                 filename=name),
            "-o" if not is_dir else "",
            "\"{local_dir}/\"".format(local_dir=self.__base_local_dir_path),
            "'"
        ])
        self.__run_command(command)

    def kill(self, name: str) -> bool:
        """
        Kill a queued or running job
        :param name:
        :return: True if job of given name was found, False otherwise
        """
        # look for this name in the status list
        job_to_kill = None
        for status in self.status():
            if status.name == name:
                job_to_kill = status
                break
        if job_to_kill is None:
            self.logger.debug("Kill failed to find job '{}'".format(name))
            return False
        # Note: there's a chance that job ids change between when we called status
        #       and when we execute the kill command
        #       in this case the wrong job may be killed, there's nothing we can do about it
        if job_to_kill.state == LftpJobStatus.State.RUNNING:
            self.logger.debug("Killing running job '{}'...".format(name))
            self.__run_command("kill {}".format(job_to_kill.id))
        elif job_to_kill.state == LftpJobStatus.State.QUEUED:
            self.logger.debug("Killing queued job '{}'...".format(name))
            self.__run_command("queue --delete {}".format(job_to_kill.id))
        else:
            raise NotImplementedError("Unsupported state {}".format(str(job_to_kill.state)))
        return True

    def kill_all(self):
        """
        Kills are jobs, queued or downloading
        :return:
        """
        # empty the queue and kill running jobs
        self.__run_command("queue -d *")
        self.__run_command("kill all")

    # Mark decorators as static (must be at end of class)
    # Source: https://stackoverflow.com/a/3422823
    with_check_process = staticmethod(with_check_process)
