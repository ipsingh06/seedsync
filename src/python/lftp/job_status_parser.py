# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import re
from typing import List
import logging

from common import AppError
from .job_status import LftpJobStatus


class LftpJobStatusParserError(AppError):
    pass


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

    __QUOTED_FILE_NAME_REGEX = "`(?P<name>.*)'"

    __QUEUE_DONE_REGEX = "^\[(?P<id>\d+)\]\sDone\s\(queue\s\(.+\)\)"

    def __init__(self):
        self.logger = logging.getLogger("LftpJobStatusParser")

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("LftpJobStatusParser")

    @staticmethod
    def _size_to_bytes(size: str) -> int:
        """
        Parse the size string and return number of bytes
        :param size:
        :return:
        """
        if size == "0":
            return 0
        m = re.compile("(?P<number>\d+\.?\d*)\s*(?P<units>{})?".format(LftpJobStatusParser.__SIZE_UNITS_REGEX))
        result = m.search(size)
        if not result:
            raise ValueError("String '{}' does not match the size pattern".format(size))
        number = float(result.group("number"))
        unit = (result.group("units") or "b")[0].lower()
        multipliers = {'b': 1, 'k': 1024, 'm': 1024*1024, 'g': 1024*1024*1024}
        if unit not in multipliers.keys():
            raise ValueError("Unrecognized unit {} in size string '{}'".format(unit, size))
        return int(number*multipliers[unit])

    @staticmethod
    def _eta_to_seconds(eta: str) -> int:
        """
        Parse the time string and return number of seconds
        :param eta:
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
        try:
            statuses += self.__parse_queue(lines)
            statuses += self.__parse_jobs(lines)
        except ValueError as e:
            self.logger.error("LftpJobStateParser error: {}".format(str(e)))
            self.logger.error("Status:\n{}".format(output))
            raise LftpJobStatusParserError("Error parsing lftp job status")
        return statuses

    @staticmethod
    def __parse_jobs(lines: List[str]) -> List[LftpJobStatus]:
        jobs = []

        # Header patterns
        # pget header
        pget_header_pattern = ("^\[(?P<id>\d+)\]\s+"
                               "pget\s+"
                               "(?P<flags>.*?)\s+"
                               "(?P<lq>['\"]|)(?P<remote>.+)(?P=lq)\s+"  # greedy on purpose
                               "-o\s+"
                               "(?P<rq>['\"]|)(?P<local>.+)(?P=rq)$")  # greedy on purpose
        pget_header_m = re.compile(pget_header_pattern)

        # mirror header (downloading)
        mirror_header_pattern = ("^\[(?P<id>\d+)\]\s+"
                                 "mirror\s+"
                                 "(?P<flags>.*?)\s+"
                                 "(?P<lq>['\"]|)(?P<remote>.+)(?P=lq)\s+"  # greedy on purpose
                                 "(?P<rq>['\"]|)(?P<local>.+)(?P=rq)\s+"  # greedy on purpose
                                 "--\s+"
                                 "(?P<szlocal>\d+\.?\d*\s?({sz})?)"  # size=0 has no units
                                 "\/"
                                 "(?P<szremote>\d+\.?\d*\s?({sz})?)\s+"  # size=0 has no units
                                 "\((?P<pctlocal>\d+)%\)"
                                 "(\s+(?P<speed>\d+\.?\d*\s?({sz}))\/s)?$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX)
        mirror_header_m = re.compile(mirror_header_pattern)

        # mirror header (connecting or receiving file list)
        mirror_fl_header_pattern = ("^\[(?P<id>\d+)\]\s+"
                                    "mirror\s+"
                                    "(?P<flags>.*?)\s+"
                                    "(?P<lq>['\"]|)(?P<remote>.+)(?P=lq)\s+"  # greedy on purpose
                                    "(?P<rq>['\"]|)(?P<local>.+)(?P=rq)$")  # greedy on purpose
        mirror_fl_header_m = re.compile(mirror_fl_header_pattern)

        # Data patterns
        filename_pattern = "\\\\transfer\s" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX
        filename_m = re.compile(filename_pattern)

        chunk_at_pattern = ("^" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX + "\s+"
                            "at\s+"
                            "\d+\s+"  # this is NOT the local size
                            "(?:\(\d+%\)\s+)?"  # this is NOT the local percent
                            "((?P<speed>\d+\.?\d*\s?({sz}))\/s\s+)?"
                            "(eta:(?P<eta>{eta})\s+)?"
                            "\s*\[(?P<desc>.*)\]$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX,
                    eta=LftpJobStatusParser.__TIME_UNITS_REGEX)
        chunk_at_m = re.compile(chunk_at_pattern)

        chunk_at2_pattern = ("^" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX + "\s+"
                             "at\s+"
                             "\d+\s+"  # this is NOT the local size
                             "(?:\(\d+%\))")  # this is NOT the local percent
        chunk_at2_m = re.compile(chunk_at2_pattern)

        chunk_got_pattern = ("^" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX + ",\s+"
                             "got\s+"
                             "(?P<szlocal>\d+)\s+"
                             "of\s+"
                             "(?P<szremote>\d+)\s+"
                             "\((?P<pctlocal>\d+)%\)"
                             "(\s+(?P<speed>\d+\.?\d*\s?({sz}))\/s)?"
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
                          "" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX + "\s+"
                          "--\s+"
                          "(?P<szlocal>\d+\.?\d*\s?({sz})?)"  # size=0 has no units
                          "\/"
                          "(?P<szremote>\d+\.?\d*\s?({sz})?)\s+"  # size=0 has no units
                          "\((?P<pctlocal>\d+)%\)"
                          "(\s+(?P<speed>\d+\.?\d*\s?({sz}))\/s)?$")\
            .format(sz=LftpJobStatusParser.__SIZE_UNITS_REGEX)
        mirror_m = re.compile(mirror_pattern)

        mirror_empty_pattern = ("\\\\mirror\s"
                                "" + LftpJobStatusParser.__QUOTED_FILE_NAME_REGEX + "\s*$")
        mirror_empty_m = re.compile(mirror_empty_pattern)

        queue_done_m = re.compile(LftpJobStatusParser.__QUEUE_DONE_REGEX)

        prev_job = None
        while lines:
            line = lines.pop(0)

            # First line must be a valid job header
            if not (
                prev_job or
                pget_header_m.match(line) or
                mirror_header_m.match(line) or
                mirror_fl_header_m.match(line)
            ):
                raise ValueError("First line is not a matching header '{}'".format(line))

            # Search for pget header
            result = pget_header_m.search(line)
            if result:
                if len(lines) < 2:
                    raise ValueError("Missing two lines of pget data for header '{}'".format(line))
                lines.pop(0)  # pop the 'sftp' line
                line = lines.pop(0)  # data line
                result_at = chunk_at_m.search(line)
                result_at2 = chunk_at2_m.search(line)
                result_got = chunk_got_m.search(line)

                id_ = int(result.group("id"))
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.PGET
                status = LftpJobStatus(job_id=id_,
                                       job_type=type_,
                                       state=LftpJobStatus.State.RUNNING,
                                       name=name,
                                       flags=flags)
                if result_at:
                    if result.group("remote") != result_at.group("name"):
                        raise ValueError("Mismatch between pget names '{}' vs '{}'".format(
                            result.group("remote"), result_at.group("name")
                        ))
                    size_local = None
                    percent_local = None
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
                elif result_at2:
                    if result.group("remote") != result_at2.group("name"):
                        raise ValueError("Mismatch between pget names '{}' vs '{}'".format(
                            result.group("remote"), result_at2.group("name")
                        ))
                    transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
                elif result_got:
                    got_group_basename = os.path.basename(os.path.normpath(result_got.group("name")))
                    if got_group_basename != name:
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, got_group_basename))
                    size_local = int(result_got.group("szlocal"))
                    size_remote = int(result_got.group("szremote"))
                    percent_local = int(result_got.group("pctlocal"))
                    speed = None
                    if result_got.group("speed"):
                        speed = LftpJobStatusParser._size_to_bytes(result_got.group("speed"))
                    eta = None
                    if result_got.group("eta"):
                        eta = LftpJobStatusParser._eta_to_seconds(result_got.group("eta"))
                    transfer_state = LftpJobStatus.TransferState(
                        size_local,
                        size_remote,
                        percent_local,
                        speed,
                        eta
                    )
                else:
                    raise ValueError("Missing chunk data for filename '{}'".format(name))
                status.total_transfer_state = transfer_state
                jobs.append(status)
                prev_job = status
                continue

            # Search for mirror header
            result = mirror_header_m.search(line)
            if result:
                id_ = int(result.group("id"))
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.MIRROR
                status = LftpJobStatus(job_id=id_,
                                       job_type=type_,
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

            # Search for mirror connecting header
            # Note: this must be after the more restrictive mirror header above
            result = mirror_fl_header_m.search(line)
            if result:
                # There may be a 'Connecting' or 'cd' line ahead, but not always
                if lines and (
                        lines[0].startswith("Getting file list") or
                        lines[0].startswith("cd ")
                ):
                    lines.pop(0)  # pop the connecting line
                id_ = int(result.group("id"))
                name = os.path.basename(os.path.normpath(result.group("remote")))
                flags = result.group("flags")
                type_ = LftpJobStatus.Type.MIRROR
                status = LftpJobStatus(job_id=id_,
                                       job_type=type_,
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
                result_at2 = chunk_at2_m.search(line)
                result_got = chunk_got_m.search(line)
                if result_at:
                    # filename is full path, but chunk name is only normpath
                    if result_at.group("name") != os.path.basename(os.path.normpath(name)):
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, result_at.group("name")))
                    size_local = None
                    percent_local = None
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
                elif result_at2:
                    # filename is full path, but chunk name is only normpath
                    if result_at2.group("name") != os.path.basename(os.path.normpath(name)):
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, result_at2.group("name")))
                    file_status = LftpJobStatus.TransferState(None, None, None, None, None)
                    prev_job.add_active_file_transfer_state(name, file_status)
                elif result_got:
                    if result_got.group("name") != os.path.basename(os.path.normpath(name)):
                        raise ValueError("Mismatch: filename '{}' but chunk data for '{}'"
                                         .format(name, result_got.group("name")))
                    size_local = int(result_got.group("szlocal"))
                    size_remote = int(result_got.group("szremote"))
                    percent_local = int(result_got.group("pctlocal"))
                    speed = None
                    if result_got.group("speed"):
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
            result = mirror_empty_m.search(line)
            if result:
                name = result.group("name")
                # One of these lines may follow, ignore it as well
                #    "Getting files list"
                #    "cd"
                #    "<name>: "
                #    "mkdir"
                if lines:
                    if "Getting file list" in lines[0] or \
                            lines[0].startswith("cd ") or \
                            lines[0] == "{}:".format(name) or \
                            lines[0].startswith("mkdir "):
                        lines.pop(0)
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

            # Search for the Done line, but it better be the last line
            result = queue_done_m.match(line)
            if result:
                if lines:
                    raise ValueError("There are more lines after the 'Done' line")
                # Continue the outer loop
                continue

            # If we got here, then we don't know how to parse this line
            raise ValueError("Unable to parse line '{}'".format(line))
        return jobs

    @staticmethod
    def __parse_queue(lines: List[str]) -> List[LftpJobStatus]:
        queue = []

        queue_done_m = re.compile(LftpJobStatusParser.__QUEUE_DONE_REGEX)
        if len(lines) == 1:
            if not queue_done_m.match(lines[0]):
                raise ValueError("Unrecognized line '{}'".format(lines[0]))
            lines.pop(0)

        if lines:
            # Look for the header lines
            if len(lines) < 2:
                raise ValueError("Missing queue header")
            header1_pattern = "^\[\d+\] queue \(sftp://.*@.*\)(?:\s+--\s+(?:\d+\.\d+|\d+)\s(?:{})\/s)?$"\
                              .format(LftpJobStatusParser.__SIZE_UNITS_REGEX)
            header2_pattern = "^sftp://.*@.*$"
            line = lines.pop(0)
            if not re.match(header1_pattern, line):
                raise ValueError("Missing queue header line 1: {}".format(line))
            line = lines.pop(0)
            if not re.match(header2_pattern, line):
                raise ValueError("Missing queue header line 2: {}".format(line))
            if not lines:
                raise ValueError("Missing queue status")

            # Look for 'Now executing' lines
            line = lines.pop(0)
            if re.match("Queue is stopped.", line):
                # Nothing to do
                pass
            elif re.match("Now executing:", line):
                # Remove any more lines associated with 'now executing'
                while lines and re.match("^-\[\d+\]", lines[0]):
                    lines.pop(0)

            # Look for the actual queue
            if lines and re.match("Commands queued:", lines[0]):
                lines.pop(0)
                if not lines:
                    raise ValueError("Missing queued commands")

                # Parse the queued commands
                queue_pget_pattern = ("^(?P<id>\d+)\.\s+"
                                      "pget\s+"
                                      "(?P<flags>.*?)\s+"
                                      "(?P<lq>[\'\"]|)(?P<remote>.+)(?P=lq)\s+"  # greedy on purpose
                                      "(?:-o\s+)"
                                      "(?P<rq>[\'\"]|)(?P<local>.+)(?P=rq)$")  # greedy on purpose
                queue_pget_m = re.compile(queue_pget_pattern)
                queue_mirror_pattern = ("^(?P<id>\d+)\.\s+"
                                        "mirror\s+"
                                        "(?P<flags>.*?)\s+"
                                        "(?P<lq>[\'\"]|)(?P<remote>.+)(?P=lq)\s+"  # greedy on purpose
                                        "(?P<rq>[\'\"]|)(?P<local>.+)(?P=rq)$")  # greedy on purpose
                queue_mirror_m = re.compile(queue_mirror_pattern)
                while lines:
                    line = lines[0]
                    if re.match("^\d+\.", line):
                        # header line
                        lines.pop(0)

                        result_pget = queue_pget_m.match(line)
                        result_mirror = queue_mirror_m.match(line)
                        if result_pget:
                            type_ = LftpJobStatus.Type.PGET
                            result = result_pget
                        elif result_mirror:
                            type_ = LftpJobStatus.Type.MIRROR
                            result = result_mirror
                        else:
                            raise ValueError("Failed to parse queue line: {}".format(line))
                        id_ = int(result.group("id"))
                        name = os.path.basename(os.path.normpath(result.group("remote")))
                        flags = result.group("flags")
                        status = LftpJobStatus(job_id=id_,
                                               job_type=type_,
                                               state=LftpJobStatus.State.QUEUED,
                                               name=name,
                                               flags=flags)
                        queue.append(status)
                    elif re.match("^cd\s.*$", line):
                        # 'cd' line after pget, ignore
                        lines.pop(0)
                    else:
                        # no match, exit loop
                        break

            # Look for the done line
            if lines and queue_done_m.match(lines[0]):
                lines.pop(0)

        return queue
