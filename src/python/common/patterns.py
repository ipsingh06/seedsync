# Copyright 2017, Inderpreet Singh, All rights reserved.

import os

from .error import PylftpError


class Patterns:
    """
    Registry of saved patterns
    Patterns are used to trigger automatic downloads
    """
    def __init__(self):
        # TODO: refactor
        self.content = []

    @staticmethod
    def from_file(patterns_file_path: str) -> "Patterns":
        patterns = Patterns()
        if not os.path.isfile(patterns_file_path):
            raise PylftpError("Patterns file not found: {}".format(patterns_file_path))
        with open(patterns_file_path) as f:
            patterns.content = [x.strip() for x in f.readlines()]
        return patterns
