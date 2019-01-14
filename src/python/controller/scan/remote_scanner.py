# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import pickle
from typing import List
import os
from typing import Optional

from .scanner_process import IScanner
from common import overrides, AppError, Localization
from ssh import Sshcp, SshcpError
from system import SystemFile


class RemoteScannerError(AppError):
    pass


class RemoteScanner(IScanner):
    """
    Scanner implementation to scan the remote filesystem
    """
    RETRY_COUNT = 5

    def __init__(self,
                 remote_address: str,
                 remote_username: str,
                 remote_password: Optional[str],
                 remote_port: int,
                 remote_path_to_scan: str,
                 local_path_to_scan_script: str,
                 remote_path_to_scan_script: str):
        self.logger = logging.getLogger("RemoteScanner")
        self.__remote_path_to_scan = remote_path_to_scan
        self.__local_path_to_scan_script = local_path_to_scan_script
        self.__remote_path_to_scan_script = remote_path_to_scan_script
        self.__ssh = Sshcp(host=remote_address,
                           port=remote_port,
                           user=remote_username,
                           password=remote_password)
        self.__first_run = True

        # Append scan script name to remote path if not there already
        script_name = os.path.basename(self.__local_path_to_scan_script)
        if os.path.basename(self.__remote_path_to_scan_script) != script_name:
            self.__remote_path_to_scan_script = os.path.join(self.__remote_path_to_scan_script, script_name)

    @overrides(IScanner)
    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("RemoteScanner")
        self.__ssh.set_base_logger(self.logger)

    @overrides(IScanner)
    def scan(self) -> List[SystemFile]:
        if self.__first_run:
            self._install_scanfs()
            self.__first_run = False

        retries = 0
        out = None
        while out is None:
            try:
                out = self.__ssh.shell("'{}' '{}'".format(
                    self.__remote_path_to_scan_script,
                    self.__remote_path_to_scan)
                )
            except SshcpError as e:
                # Suppress specific errors and retry a fixed number of times
                # Otherwise raise a fatal AppError
                if RemoteScanner.__suppress_error(e) and retries < RemoteScanner.RETRY_COUNT:
                    self.logger.warning("Retrying remote scan after error: {}".format(str(e)))
                    out = None
                    retries += 1
                else:
                    self.logger.exception("Caught an SshError")
                    raise AppError(Localization.Error.REMOTE_SERVER_SCAN)

        try:
            remote_files = pickle.loads(out)
        except pickle.UnpicklingError as err:
            self.logger.error("Unpickling error: {}\n{}".format(str(err), out))
            raise AppError(Localization.Error.REMOTE_SERVER_SCAN)
        return remote_files

    def _install_scanfs(self):
        self.logger.info("Installing local:{} to remote:{}".format(
            self.__local_path_to_scan_script,
            self.__remote_path_to_scan_script
        ))
        if not os.path.isfile(self.__local_path_to_scan_script):
            raise RemoteScannerError("Failed to find scanfs executable at {}".format(
                self.__local_path_to_scan_script
            ))
        try:
            self.__ssh.copy(local_path=self.__local_path_to_scan_script,
                            remote_path=self.__remote_path_to_scan_script)
        except SshcpError:
            self.logger.exception("Caught scp exception")
            raise AppError(Localization.Error.REMOTE_SERVER_INSTALL)

    @staticmethod
    def __suppress_error(error: SshcpError) -> bool:
        error_str = str(error).lower()
        errors_to_suppress = [
            "text file busy",
            "ssh_exchange_identification",
            "cannot create temporary directory",
            "connection timed out"
        ]
        return any(e in error_str for e in errors_to_suppress)
