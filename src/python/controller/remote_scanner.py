# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import pickle
from typing import List

from .scanner_process import IScanner
from common import overrides
from ssh import Ssh
from system import SystemFile


class RemoteScanner(IScanner):
    """
    Scanner implementation to scan the remote filesystem
    """
    def __init__(self,
                 remote_address: str,
                 remote_username: str,
                 remote_path_to_scan: str,
                 remote_path_to_scan_script: str):
        self.__remote_path_to_scan = remote_path_to_scan
        self.__ssh = Ssh(host=remote_address,
                         user=remote_username,
                         target_dir=remote_path_to_scan_script)

    def set_base_logger(self, base_logger: logging.Logger):
        self.__ssh.set_base_logger(base_logger)

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        out = self.__ssh.run_command("python3 scan_fs.py {}".format(self.__remote_path_to_scan))
        remote_files = pickle.loads(out)
        return remote_files
