# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from typing import List

from .scanner_process import IScanner
from common import overrides
from system import SystemScanner, SystemFile


class LocalScanner(IScanner):
    """
    Scanner implementation to scan the local filesystem
    """
    def __init__(self, local_path: str):
        self.__scanner = SystemScanner(local_path)

    def set_base_logger(self, base_logger: logging.Logger):
        pass

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        return self.__scanner.scan()
