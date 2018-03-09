# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
from typing import List

from .scanner_process import IScanner
from common import overrides, AppError, Localization, Constants
from system import SystemScanner, SystemFile, SystemScannerError


class LocalScanner(IScanner):
    """
    Scanner implementation to scan the local filesystem
    """
    def __init__(self, local_path: str, use_temp_file: bool):
        self.__scanner = SystemScanner(local_path)
        if use_temp_file:
            self.__scanner.set_lftp_temp_suffix(Constants.LFTP_TEMP_FILE_SUFFIX)
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
            raise AppError(Localization.Error.LOCAL_SERVER_SCAN)
        return result
