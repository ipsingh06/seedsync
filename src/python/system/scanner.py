# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import re
from typing import List

# my libs
from .file import SystemFile


class SystemScanner:
    """
    Scans system (local or remote) to generate list of files and sizes
    """
    __LFTP_STATUS_FILE_SUFFIX = ".lftp-pget-status"

    def __init__(self, path_to_scan: str):
        if not os.path.isdir(path_to_scan):
            raise ValueError("Path to scan is not a directory: {}".format(path_to_scan))
        self.path_to_scan = path_to_scan
        self.exclude_prefixes = []
        self.exclude_suffixes = [SystemScanner.__LFTP_STATUS_FILE_SUFFIX]
        self.root_filters = []

    def add_root_filter(self, file_name: str):
        """
        Add a file name filter. Only filtered files will be included in the scan.
        The filter applies only at the root level. I.e., all files in a filtered
        directory are included
        Note: exclude prefix/suffix will be ignored for filtering. They will
              however be applied for a filtered directory's children
        :param file_name:
        :return:
        """
        self.root_filters.append(file_name)

    def clear_root_filters(self):
        """
        Clear the filters. All files will be scanned.
        :return:
        """
        self.root_filters.clear()

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

    def scan(self) -> List[SystemFile]:
        """
        Scan the path to generate list of system files
        The files and its children are inserted in alphabetical order
        :return:
        """
        def create_children(path: str):
            children = []
            for entry in os.scandir(path):
                # Skip excluded entries
                skip = False
                # Check for filters, but only at the root level
                if self.root_filters and path == self.path_to_scan:
                    if entry.name not in self.root_filters:
                        skip = True
                else:
                    for prefix in self.exclude_prefixes:
                        if entry.name.startswith(prefix):
                            skip = True
                            break
                    for suffix in self.exclude_suffixes:
                        if entry.name.endswith(suffix):
                            skip = True
                            break
                if skip:
                    continue

                if entry.is_dir():
                    sub_children = create_children(entry.path)
                    size = sum(sub_child.size for sub_child in sub_children)
                    sf = SystemFile(entry.name, size, True)
                    for sub_child in sub_children:
                        sf.add_child(sub_child)
                else:
                    file_size = entry.stat().st_size
                    # Check if it's a partial lftp file, and if so, use the lftp
                    # status to get the real file size
                    lftp_status_file_path = entry.path + SystemScanner.__LFTP_STATUS_FILE_SUFFIX
                    if os.path.isfile(lftp_status_file_path):
                        with open(lftp_status_file_path, "r") as f:
                            file_size = SystemScanner._lftp_status_file_size(f.read())
                    sf = SystemFile(entry.name, file_size, False)
                children.append(sf)
            children.sort(key=lambda f: f.name)
            return children

        return create_children(self.path_to_scan)

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
        total_size = None
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
