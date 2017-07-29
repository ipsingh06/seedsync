# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
from typing import List

# my libs
from .file import SystemFile


class SystemScanner:
    """
    Scans system (local or remote) to generate list of files and sizes
    """
    def __init__(self, path_to_scan: str):
        if not os.path.isdir(path_to_scan):
            raise ValueError("Path to scan is not a directory: {}".format(path_to_scan))
        self.path_to_scan = path_to_scan
        self.exclude_prefixes = []
        self.exclude_suffixes = []

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
                    sf = SystemFile(entry.name, entry.stat().st_size, False)
                children.append(sf)
            children.sort(key=lambda f: f.name)
            return children

        return create_children(self.path_to_scan)
