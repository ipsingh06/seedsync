# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import re
from typing import List
from datetime import datetime

# my libs
from common import AppError
from .file import SystemFile


class SystemScannerError(AppError):
    """
    Exception indicating a bad config value
    """
    pass


class PseudoDirEntry:
    def __init__(self, name: str, path: str, is_dir: bool, stat):
        self.name = name
        self.path = path
        self._is_dir = is_dir
        self._stat = stat

    def is_dir(self):
        return self._is_dir

    def stat(self):
        return self._stat


class SystemScanner:
    """
    Scans system to generate list of files and sizes
    Children are returned in alphabetical order
    """
    __LFTP_STATUS_FILE_SUFFIX = ".lftp-pget-status"

    def __init__(self, path_to_scan: str):
        """
        :param path_to_scan: path to file or directory to scan
        """
        self.path_to_scan = path_to_scan
        self.exclude_prefixes = []
        self.exclude_suffixes = [SystemScanner.__LFTP_STATUS_FILE_SUFFIX]
        self.__lftp_temp_file_suffix = None

    def add_exclude_prefix(self, prefix: str):
        """
        Exclude files that begin with the given prefix
        :param prefix:
        :return:
        """
        self.exclude_prefixes.append(prefix)

    def add_exclude_suffix(self, suffix: str):
        """
        Exclude files that end with the given suffix
        :param suffix:
        :return:
        """
        self.exclude_suffixes.append(suffix)

    def set_lftp_temp_suffix(self, suffix: str):
        """
        Set the suffix used by LFTP temp files
        Scanner will ignore the suffix and show these files with their
        original name
        :return:
        """
        self.__lftp_temp_file_suffix = suffix

    def scan(self) -> List[SystemFile]:
        """
        Scan the path to generate list of system files
        :return:
        """
        if not os.path.exists(self.path_to_scan):
            raise SystemScannerError("Path does not exist: {}".format(self.path_to_scan))
        elif not os.path.isdir(self.path_to_scan):
            raise SystemScannerError("Path is not a directory: {}".format(self.path_to_scan))
        return self.__create_children(self.path_to_scan)

    def scan_single(self, name: str) -> SystemFile:
        """
        Scan a single file/dir
        :param name:
        :return:
        """
        path = os.path.join(self.path_to_scan, name)
        temp_path = (path + self.__lftp_temp_file_suffix) if self.__lftp_temp_file_suffix else None

        if os.path.exists(path):
            # We're good to go
            pass
        elif temp_path and os.path.isfile(temp_path):
            # There's a temp file, use that
            path = temp_path
        else:
            raise SystemScannerError("Path does not exist: {}".format(path))

        return self.__create_system_file(
            PseudoDirEntry(
                name=name,
                path=path,
                is_dir=os.path.isdir(path),
                stat=os.stat(path)
            )
        )

    def __create_system_file(self, entry) -> SystemFile:
        """
        Creates a system file from a DirEntry.

        Note:
             Strips out any characters not-supported in utf-8. This prevents problems
             in other systems.

        Args:
            entry: DirEntry object

        Returns:
            The SystemFile object
        """
        if entry.is_dir():
            sub_children = self.__create_children(entry.path)
            name = entry.name.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
            size = sum(sub_child.size for sub_child in sub_children)
            time_created = None
            try:
                time_created = datetime.fromtimestamp(entry.stat().st_birthtime)
            except AttributeError:
                pass
            time_modified = datetime.fromtimestamp(entry.stat().st_mtime)
            sys_file = SystemFile(name,
                                  size,
                                  True,
                                  time_created=time_created,
                                  time_modified=time_modified)
            for sub_child in sub_children:
                sys_file.add_child(sub_child)
        else:
            file_size = entry.stat().st_size
            # Check if it's a partial lftp file, and if so, use the lftp
            # status to get the real file size
            lftp_status_file_path = entry.path + SystemScanner.__LFTP_STATUS_FILE_SUFFIX
            if os.path.isfile(lftp_status_file_path):
                with open(lftp_status_file_path, "r") as f:
                    file_size = SystemScanner._lftp_status_file_size(f.read())
            # Check to see if this is a lftp temp file, and if so, use the real name
            file_name = entry.name.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
            if self.__lftp_temp_file_suffix is not None and \
                    file_name != self.__lftp_temp_file_suffix and \
                    file_name.endswith(self.__lftp_temp_file_suffix):
                file_name = file_name[:-len(self.__lftp_temp_file_suffix)]
            time_created = None
            try:
                time_created = datetime.fromtimestamp(entry.stat().st_birthtime)
            except AttributeError:
                pass
            time_modified = datetime.fromtimestamp(entry.stat().st_mtime)
            sys_file = SystemFile(file_name,
                                  file_size,
                                  False,
                                  time_created=time_created,
                                  time_modified=time_modified)
        return sys_file

    def __create_children(self, path: str) -> List[SystemFile]:
        children = []
        # Files may get deleted while scanning, ignore the error
        for entry in os.scandir(path):
            # Skip excluded entries
            skip = False
            for prefix in self.exclude_prefixes:
                if entry.name.startswith(prefix):
                    skip = True
            for suffix in self.exclude_suffixes:
                if entry.name.endswith(suffix):
                    skip = True
            if skip:
                continue

            try:
                sys_file = self.__create_system_file(entry)
            except FileNotFoundError:
                continue
            children.append(sys_file)
        children.sort(key=lambda fl: fl.name)
        return children

    @staticmethod
    def _lftp_status_file_size(status: str) -> int:
        """
        Returns the real file size as indicated by an lftp status content
        :param status:
        :return:
        """
        size_pattern_m = re.compile("^size=(\d+)$")
        pos_pattern_m = re.compile("^\d+\.pos=(\d+)$")
        limit_pattern_m = re.compile("^\d+\.limit=(\d+)$")
        lines = [s.strip() for s in status.splitlines()]
        lines = list(filter(None, lines))  # remove blank lines
        if not lines:
            return 0

        empty_size = 0
        # First line should be a size
        result = size_pattern_m.search(lines[0])
        if not result:
            return 0
        total_size = int(result.group(1))
        lines.pop(0)
        while lines:
            # There should be pairs of lines
            if len(lines) < 2:
                return 0
            result_pos = pos_pattern_m.search(lines[0])
            result_limit = limit_pattern_m.search(lines[1])
            if not result_pos or not result_limit:
                return 0
            pos = int(result_pos.group(1))
            limit = int(result_limit.group(1))
            empty_size += limit - pos
            lines.pop(0)
            lines.pop(0)

        return total_size-empty_size
