# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from typing import List

from .scanner_process import IScanner
from common import overrides, PylftpError, Localization
from system import SystemScanner, SystemFile, SystemScannerError


class LocalScanner(IScanner):
    """
    Scanner implementation to scan the local filesystem
    """
    def __init__(self, local_path: str):
        self.__scanner = SystemScanner(local_path)
        self.logger = logging.getLogger("LocalScanner")

    @overrides(IScanner)
    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("LocalScanner")

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        try:
            result = self.__scanner.scan()
        except SystemScannerError:
            self.logger.exception("Caught SystemScannerError")
            raise PylftpError(Localization.Error.LOCAL_SERVER_SCAN)
        return result
