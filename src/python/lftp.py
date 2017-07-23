# Copyright 2017, Inderpreet Singh, All rights reserved.

from enum import Enum
import os
import re
import logging
from functools import wraps
from collections import namedtuple
from typing import Callable, Union, List

# 3rd party libs
import pexpect


class LftpError(Exception):
    """
    Custom exception that describes the failure of the lftp command
    """
    pass


class LftpJobStatus:
    """
    Represents the status of a single Lftp jobs
    """
    class Type(Enum):
        MIRROR = "mirror"
        PGET = "pget"

    class State(Enum):
        QUEUED = 0
        RUNNING = 1

    class TransferState(namedtuple("TransferState",
                                   ["size_local",
                                    "size_remote",
                                    "percent_local",
                                    "speed",
                                    "eta"])):
        """
        State of transfer for a file or entire download
          size_local: size in bytes that have been downloaded
          size_remote: size in bytes on the remote server (may not be available)
          percent_local: percent of bytes that have been downloaded (0-100)
          speed: transfer speed in bytes per second
          eta: est. remaining transfer time in seconds
        """
        pass

    def __init__(self, job_type: Type, state: State, name: str, flags: str):
        self.__type = job_type
        self.__state = state
        self.__name = name
        self.__flags = flags
        self.__total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        # dict of active file transfer states, maps filename to their transfer state
        # there's no hierarchical info for now
        self.__active_files_state = {}

    @property
    def type(self) -> Type: return self.__type

    @property
    def state(self) -> "LftpJobStatus.State": return self.__state

    @property
    def name(self) -> str: return self.__name

    @property
    def total_transfer_state(self) -> TransferState:
        return self.__total_transfer_state

    @total_transfer_state.setter
    def total_transfer_state(self, total_transfer_state: TransferState):
        if self.__state == LftpJobStatus.State.QUEUED:
            raise TypeError("Cannot set transfer state on job of type queue")
        self.__total_transfer_state = total_transfer_state

    def add_active_file_transfer_state(self, filename: str, transfer_state: TransferState):
        if self.__state == LftpJobStatus.State.QUEUED:
            raise TypeError("Cannot set transfer state on job of type queue")
        self.__active_files_state[filename] = transfer_state

    def get_active_file_transfer_states(self):
        """
        Returns list of pairs (filename, transfer state)
        :return:
        """
        return list(zip(self.__active_files_state.keys(), self.__active_files_state.values()))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class LftpJobStatusParser:
    """
    Parses the output of lftp's "jobs -v" command into a LftpJobStatus
    """
    # python doesn't support partial inline-modified flags, so we need
    # to capture all case-sensitive cases here
    __SIZE_UNITS_REGEX = ("b|B|"
                          "k|kb|kib|K|Kb|KB|KiB|Kib|"
                          "m|mb|mib|M|Mb|MB|MiB|Mib|"
                          "g|gb|gib|G|Gb|GB|GiB|Gib")
    __TIME_UNITS_REGEX = "(?P<eta_d>\d*d)?(?P<eta_h>\d*h)?(?P<eta_m>\d*m)?(?P<eta_s>\d*s)?"

    def __init__(self):
        pass

    @staticmethod
    def _size_to_bytes(size: str) -> int:
        """
        Parse the size string and return number of bytes
        :param size:
        :return:
        """
        if size == "0":
            return 0
        m = re.compile("(?P<number>\d+\.?\d*)\s*(?P<units>{})".format(LftpJobStatusParser.__SIZE_UNITS_REGEX))
        result = m.search(size)
        if not result:
            raise ValueError("String '{}' does not match the size pattern".format(size))
        number = float(result.group("number"))
        unit = result.group("units")[0].lower()
        multipliers = {'b': 1, 'k': 1024, 'm': 1024*1024, 'g': 1024*1024*1024}
        if unit not in multipliers.keys():
            raise ValueError("Unrecognized unit {} in size string '{}'".format(unit, size))
        return int(number*multipliers[unit])

    @staticmethod
    def _eta_to_seconds(eta: str) -> int:
        """
        Parse the time string and return number of seconds
        :param time:
        :return:
        """
        m = re.compile(LftpJobStatusParser.__TIME_UNITS_REGEX)
        result = m.search(eta)
        if not result:
            raise ValueError("String '{}' does not match the eta pattern".format(eta))
        # the [:-1] below remove the last character
        eta_d = int((result.group("eta_d") or '0d')[:-1])
        eta_h = int((result.group("eta_h") or '0h')[:-1])
        eta_m = int((result.group("eta_m") or '0m')[:-1])
        eta_s = int((result.group("eta_s") or '0s')[:-1])
        return eta_d*24*3600 + eta_h*3600 + eta_m*60 + eta_s

    def parse(self, output: str) -> List[LftpJobStatus]:
        statuses = list()
        lines = [s.strip() for s in output.splitlines()]
        lines = list(filter(None, lines))  # remove blank lines
        statuses += self.__parse_queue(lines)
        statuses += self.__parse_jobs(lines)
        return statuses

    @staticmethod
    def __parse_jobs(lines: List[str]) -> List[LftpJobStatus]:
        jobs = []

        # Header patterns
        pget_header_pattern = ("^\[(?P<num>\d+)\]\s+"
                               "pget\s+"
                               "(?P<flags>.*?)\s+"
                               "(?P<lq>['\"])?(?P<remote>[^\"']*?)(?P=lq)?\s+"
                               "-o\s+"
                               "(?P<rq>['\"])?(?P<local>[^\"']*)(?P=rq)?$")
        pget_header_m = re.compile(pget_header_pattern)

        mirror_header_pattern = ("^\[(?P<num>\d+)\]\s+"
                                 "mirror\s+"
                                 "(?P<flags>.*?)\s+"
                                 "(?P<lq>['\"])?(?P<remote>[^\"']+)(?P=lq)?\s+"
                                 "(?P<rq>['\"])?(?P<local>[^\"']+)(?P=rq)?\s+"
                                 "--\s+"
                                 "(?P<szlocal>\d+\.?\d*\s?({sz})?)"  # size=0 has no units
                                 "\/"
                                 "(?P<szremote>\d+\.?\d*\s?({sz}))\s+"
                                 "\((?P<pctlocal>\d+)%\)"
                                 "(\s+(?P<speed>\d+\.?\d*\s?({sz}))\/s)?$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX)
        mirror_header_m = re.compile(mirror_header_pattern)

        mirror_fl_header_pattern = ("^\[(?P<num>\d+)\]\s+"
                                    "mirror\s+"
                                    "(?P<flags>.*?)\s+"
                                    "(?P<lq>['\"])?(?P<remote>[^\"']+)(?P=lq)?\s+"
                                    "(?P<rq>['\"])?(?P<local>[^\"']+)(?P=rq)?$")
        mirror_fl_header_m = re.compile(mirror_fl_header_pattern)

        # Data patterns
        filename_pattern = "\\\\transfer\s`(?P<name>[^']*)'"
        filename_m = re.compile(filename_pattern)

        chunk_at_pattern = ("^`(?P<name>[^']*?)'\s+"
                            "at\s+"
                            "(?P<szlocal>\d+)\s+"
                            "\((?P<pctlocal>\d+)%\)\s+"
                            "((?P<speed>\d+\.?\d*\s?({sz}))\/s\s+)?"
                            "(eta:(?P<eta>{eta})\s+)?"
                            "\[(?P<desc>.*)\]$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX,
                    eta=LftpJobStatusParser.__TIME_UNITS_REGEX)
        chunk_at_m = re.compile(chunk_at_pattern)

        chunk_got_pattern = ("^`(?P<name>[^']*?)',\s+"
                             "got\s+"
                             "(?P<szlocal>\d+)\s+"
                             "of\s+"
                             "(?P<szremote>\d+)\s+"
                             "\((?P<pctlocal>\d+)%\)\s+"
                             "(?P<speed>\d+\.?\d*\s?({sz}))\/s"
                             "(\seta:(?P<eta>{eta}))?")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX,
                    eta=LftpJobStatusParser.__TIME_UNITS_REGEX)
        chunk_got_m = re.compile(chunk_got_pattern)

        chunk_header_pattern = ("\\\\chunk\s"
                                "(?P<start>\d+)"
                                "-"
                                "(?P<end>\d+)")
        chunk_header_m = re.compile(chunk_header_pattern)

        mirror_pattern = ("\\\\mirror\s"
                          "`(?P<name>[^']*)'\s+"
                          "--\s+"
                          "(?P<szlocal>\d+\.?\d*\s?({sz}))"
                          "\/"
                          "(?P<szremote>\d+\.?\d*\s?({sz}))\s+"
                          "\((?P<pctlocal>\d+)%\)"
                          "(\s+(?P<speed>\d+\.?\d*\s?({sz}))\/s)?$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX)
        mirror_m = re.compile(mirror_pattern)

        prev_job = None
        while lines:
            line = lines.pop(0)

            # First line must be a valid job header
            if not prev_job and \
                not pget_header_m.match(line) and \
                not mirror_header_m.match(line) and \
                not mirror_fl_header_m.match(line):
                raise ValueError("First line is not a matching header '{}'".format(line))

            # Search for pget header
            result = pget_header_m.search(line)
            if result:
                if len(lines) < 2:
                    raise ValueError("Missing two lines of pget data for header '{}'".format(line))
                lines.pop(0)  # pop the 'sftp' line
                line = lines.pop(0)  # data line
                result_at = chunk_at_m.search(line)
                if not result_at:
                    raise ValueError("Invalid pget data line '{}'".format(line))
                if result.group("remote") != result_at.group("name"):
                    raise ValueError("Mismatch between pget names '{}' vs '{}'".format(
                        result.group("remote"), result_at.group("name")
                    ))
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.PGET
                status = LftpJobStatus(job_type=type_,
                                       state=LftpJobStatus.State.RUNNING,
                                       name=name,
                                       flags=flags)
                size_local = int(result_at.group("szlocal"))
                percent_local = int(result_at.group("pctlocal"))
                speed = None
                if result_at.group("speed"):
                    speed = LftpJobStatusParser._size_to_bytes(result_at.group("speed"))
                eta = None
                if result_at.group("eta"):
                    eta = LftpJobStatusParser._eta_to_seconds(result_at.group("eta"))
                transfer_state = LftpJobStatus.TransferState(
                    size_local,
                    None,  # size remote
                    percent_local,
                    speed,
                    eta
                )
                status.total_transfer_state = transfer_state
                jobs.append(status)
                prev_job = status
                continue

            # Search for mirror header
            result = mirror_header_m.search(line)
            if result:
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.MIRROR
                status = LftpJobStatus(job_type=type_,
                                       state=LftpJobStatus.State.RUNNING,
                                       name=name,
                                       flags=flags)
                size_local = LftpJobStatusParser._size_to_bytes(result.group("szlocal"))
                size_remote = LftpJobStatusParser._size_to_bytes(result.group("szremote"))
                percent_local = int(result.group("pctlocal"))
                speed = None
                if result.group("speed"):
                    speed = LftpJobStatusParser._size_to_bytes(result.group("speed"))
                transfer_state = LftpJobStatus.TransferState(
                    size_local,
                    size_remote,
                    percent_local,
                    speed,
                    None  # eta
                )
                status.total_transfer_state = transfer_state
                jobs.append(status)
                prev_job = status
                # Continue the outer loop
                continue

            # Search for mirror receiving file list header
            # Note: this must be after the more restrictive mirror header above
            result = mirror_fl_header_m.search(line)
            if result:
                if not lines or not lines[0].startswith("Getting file list"):
                    raise ValueError("Missing expected 'Getting file list' line after mirror header")
                lines.pop(0)  # pop the 'getting file list' line
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.MIRROR
                status = LftpJobStatus(job_type=type_,
                                       state=LftpJobStatus.State.RUNNING,
                                       name=name,
                                       flags=flags)
                jobs.append(status)
                prev_job = status
                # Continue the outer loop
                continue

            # Search for filename
            result = filename_m.search(line)
            if result:
                name = result.group("name")
                if not lines:
                    raise ValueError("Missing chunk data for filename '{}'".format(name))
                line = lines.pop(0)
                result_at = chunk_at_m.search(line)
                result_got = chunk_got_m.search(line)
                if result_at:
                    # filename is full path, but chunk name is only normpath
                    if result_at.group("name") != os.path.basename(os.path.normpath(name)):
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, result_at.group("name")))
                    size_local = int(result_at.group("szlocal"))
                    percent_local = int(result_at.group("pctlocal"))
                    speed = None
                    if result_at.group("speed"):
                        speed = LftpJobStatusParser._size_to_bytes(result_at.group("speed"))
                    eta = None
                    if result_at.group("eta"):
                        eta = LftpJobStatusParser._eta_to_seconds(result_at.group("eta"))
                    file_status = LftpJobStatus.TransferState(
                        size_local,
                        None,
                        percent_local,
                        speed,
                        eta
                    )
                    prev_job.add_active_file_transfer_state(name, file_status)
                elif result_got:
                    if result_got.group("name") != os.path.basename(os.path.normpath(name)):
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, result_got.group("name")))
                    size_local = int(result_got.group("szlocal"))
                    size_remote = int(result_got.group("szremote"))
                    percent_local = int(result_got.group("pctlocal"))
                    speed = LftpJobStatusParser._size_to_bytes(result_got.group("speed"))
                    eta = None
                    if result_got.group("eta"):
                        eta = LftpJobStatusParser._eta_to_seconds(result_got.group("eta"))
                    file_status = LftpJobStatus.TransferState(
                        size_local,
                        size_remote,
                        percent_local,
                        speed,
                        eta
                    )
                    prev_job.add_active_file_transfer_state(name, file_status)
                else:
                    raise ValueError("Missing chunk data for filename '{}'".format(name))
                # Continue the outer loop
                continue

            # Search for but ignore "\mirror" line
            result = mirror_m.search(line)
            if result:
                # Continue the outer loop
                continue

            # Search for but ignore "\chunk" line
            result = chunk_header_m.search(line)
            if result:
                # Also need to ignore the next line
                if not lines:
                    raise ValueError("Missing data line for chunk '{}'".format(line))
                lines.pop(0)
                # Continue the outer loop
                continue

            # If we got here, then we don't know how to parse this line
            raise ValueError("Unable to parse line '{}'".format(line))
        return jobs

    @staticmethod
    def __parse_queue(lines: List[str]) -> List[LftpJobStatus]:
        queue = []

        queue_done_pattern = "^\[(?P<num>\d+)\]\sDone\s\(queue\s\(.+\)\)"
        queue_done_m = re.compile(queue_done_pattern)
        if len(lines) == 1:
            if not queue_done_m.match(lines[0]):
                raise ValueError("Unrecognized line '{}'".format(lines[0]))
            lines.pop(0)

        if lines:
            if len(lines) < 2:
                raise ValueError("Missing queue header")
            header1_pattern = "^\[\d+\] queue \(sftp://.*@.*\)(?:\s+--\s+(?:\d+\.\d+|\d+)\s(?:{})\/s)?$"\
                              .format(LftpJobStatusParser.__SIZE_UNITS_REGEX)
            header2_pattern = "^sftp://.*@.*$"
            if not re.match(header1_pattern, lines.pop(0)):
                raise ValueError("Missing queue header line 1")
            if not re.match(header2_pattern, lines.pop(0)):
                raise ValueError("Missing queue header line 2")
            if not lines:
                raise ValueError("Missing queue status")
            line = lines.pop(0)
            if not re.match("Queue is stopped.", line):
                if not re.match("Now executing:", line):
                    raise ValueError("Missing queue status")
                while lines and re.match("^-\[\d+\]", lines[0]):
                    lines.pop(0)
            if lines and re.match("Commands queued:", lines[0]):
                lines.pop(0)
                if not lines:
                    raise ValueError("Missing queued commands")

                # Parse the queued commands
                queue_pattern = ("^\d+\.\s+"
                                 "(?P<type>mirror|pget)\s+"
                                 "(?P<flags>.*?)\s+"
                                 "(?P<lq>['\"])?(?P<remote>[^\"']*?)(?P=lq)?\s+"
                                 "(?:-o\s+)?"
                                 "(?P<rq>['\"])?(?P<local>[^\"']*)(?P=rq)?$")
                m = re.compile(queue_pattern)
                while lines and re.match("^\d+\.", lines[0]):
                    line = lines.pop(0)
                    result = m.search(line)
                    if not result:
                        raise ValueError("Failed to parse queue line: {}".format(line))
                    name = os.path.basename(os.path.normpath(result.group("remote")))
                    flags = result.group("flags")
                    type_ = LftpJobStatus.Type(result.group("type"))
                    status = LftpJobStatus(job_type=type_,
                                           state=LftpJobStatus.State.QUEUED,
                                           name=name,
                                           flags=flags)
                    queue.append(status)
        return queue


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
