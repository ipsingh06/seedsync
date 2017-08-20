# Copyright 2017, Inderpreet Singh, All rights reserved.

import os

from .error import PylftpError


class Patterns:
    """
    Registry of saved patterns
    Patterns are used to trigger automatic downloads
    """
    def __init__(self):
        self.lines = []

    @staticmethod
    def from_file(patterns_file_path: str) -> "Patterns":
        patterns = Patterns()
        if not os.path.isfile(patterns_file_path):
            raise PylftpError("Patterns file not found: {}".format(patterns_file_path))
        with open(patterns_file_path) as f:
            patterns.lines = [x.strip() for x in f.readlines()]
            patterns.lines = [x for x in patterns.lines if x]  # remove empty lines
        return patterns
