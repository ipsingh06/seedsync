# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import re
from functools import wraps
from typing import Callable, Union

# 3rd party libs
import pexpect


class LftpError(Exception):
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
    __SET_RATE_LIMIT = "net:limit-rate"
    __SET_MIN_CHUNK_SIZE = "pget:min-chunk-size"
    __SET_NUM_PARALLEL_JOBS = "cmd:queue-parallel"

    def __init__(self, address: str, user: str, password: str):
        self.__user = user
        self.__password = password
        self.__address = address
        self.__base_remote_dir_path = ""
        self.__base_local_dir_path = ""
        self.logger = logging.getLogger("Lftp")
        self.__expect_pattern = "lftp {}@{}:.*>".format(self.__user, self.__address)

        args = [
            "-u", "{},{}".format(self.__user, self.__password),
            "sftp://{}".format(self.__address)
        ]
        self.__process = pexpect.spawn("/usr/bin/lftp", args)
        self.__process.expect(self.__expect_pattern)

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

    def set_base_remote_dir_path(self, base_remote_dir_path: str):
        self.__base_remote_dir_path = base_remote_dir_path

    def set_base_local_dir_path(self, base_local_dir_path: str):
        self.__base_local_dir_path = base_local_dir_path

    @with_check_process
    def __set(self, setting: str, value: str):
        """
        Set a setting in the lftp runtime
        :param setting:
        :param value:
        :return:
        """
        self.__process.sendline("set {} {}".format(setting, value))
        self.__process.expect(self.__expect_pattern)

    @with_check_process
    def __get(self, setting: str) -> str:
        """
        Get a setting from the lftp runtime
        :param setting:
        :return:
        """
        self.__process.sendline("set -a | grep {}".format(setting))
        self.__process.expect(self.__expect_pattern)
        out = self.__process.before.decode()
        m = re.search("set {} (.*)".format(setting), out)
        if not m or not m.group or not m.group(1):
            raise LftpError("Failed to get setting '{}'. Output: '{}'".format(setting, out))
        return m.group(1).strip()

    def set_num_connections(self, num_connections: int):
        if num_connections < 1:
            raise ValueError("Number of connections must be positive")
        self.__set(Lftp.__SET_NUM_CONNECTIONS_PGET, str(num_connections))
        self.__set(Lftp.__SET_NUM_CONNECTIONS_MIRROR, str(num_connections))

    def get_num_connections(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_CONNECTIONS_MIRROR))

    def set_num_parallel_files(self, num_parallel_files: int):
        if num_parallel_files < 1:
            raise ValueError("Number of parallel files must be positive")
        self.__set(Lftp.__SET_NUM_PARALLEL_FILES, str(num_parallel_files))

    def get_num_parallel_files(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_PARALLEL_FILES))

    def set_rate_limit(self, rate_limit: Union[int, str]):
        self.__set(Lftp.__SET_RATE_LIMIT, str(rate_limit))

    def get_rate_limit(self) -> str:
        return self.__get(Lftp.__SET_RATE_LIMIT)

    def set_min_chunk_size(self, min_chunk_size: Union[int, str]):
        self.__set(Lftp.__SET_MIN_CHUNK_SIZE, str(min_chunk_size))

    def get_min_chunk_size(self) -> str:
        return self.__get(Lftp.__SET_MIN_CHUNK_SIZE)

    def set_num_parallel_jobs(self, num_parallel_jobs: int):
        if num_parallel_jobs < 1:
            raise ValueError("Number of parallel jobs must be positive")
        self.__set(Lftp.__SET_NUM_PARALLEL_JOBS, str(num_parallel_jobs))

    def get_num_parallel_jobs(self) -> int:
        return int(self.__get(Lftp.__SET_NUM_PARALLEL_JOBS))

    # Mark decorators as static (must be at end of class)
    # Source: https://stackoverflow.com/a/3422823
    with_check_process = staticmethod(with_check_process)

    # def start_download(self, filename, is_file: bool):
    #     if self.__process is not None:
    #         raise LftpError("An lftp process is already running")
    #
    #     if is_file:
    #         command_template = (
    #             "/usr/bin/lftp -u {user},pass "
    #             "sftp://{address} -e "
    #             "\"pget -c -n {num_conn} "
    #             "\\\"{remote_dir}/{filename}\\\" -o {local_dir}/; exit\""
    #         )
    #     else:
    #         command_template = (
    #             "/usr/bin/lftp -u {user},pass "
    #             "sftp://{address} -e "
    #             "\"mirror -c --parallel={num_paral} --use-pget-n={num_conn} "
    #             "\\\"{remote_dir}/{filename}\\\" {local_dir}/; exit\""
    #         )
    #     command = command_template.format(
    #         user=self.__user,
    #         address= self.__address,
    #         num_paral=self.__num_parallel_files,
    #         num_conn=self.__num_connections,
    #         remote_dir=self.__base_remote_dir_path,
    #         filename=filename,
    #         local_dir=self.__base_local_dir_path
    #     )
    #     self.logger.debug("Command: {}".format(command))
