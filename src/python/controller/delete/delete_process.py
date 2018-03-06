# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import shutil

from common import AppOneShotProcess
from ssh import Ssh, SshError


class DeleteLocalProcess(AppOneShotProcess):
    def __init__(self, local_path: str, file_name: str):
        super().__init__(name=self.__class__.__name__)
        self.__local_path = local_path
        self.__file_name = file_name

    def run_once(self):
        file_path = os.path.join(self.__local_path, self.__file_name)
        self.logger.debug("Deleting local file {}".format(self.__file_name))
        if not os.path.exists(file_path):
            self.logger.error("Failed to delete non-existing file: {}".format(file_path))
        else:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)


class DeleteRemoteProcess(AppOneShotProcess):
    def __init__(self,
                 remote_address: str,
                 remote_username: str,
                 remote_port: int,
                 remote_path: str,
                 file_name: str):
        super().__init__(name=self.__class__.__name__)
        self.__remote_path = remote_path
        self.__file_name = file_name
        self.__ssh = Ssh(host=remote_address,
                         port=remote_port,
                         user=remote_username)

    def run_once(self):
        self.__ssh.set_base_logger(self.logger)
        file_path = os.path.join(self.__remote_path, self.__file_name)
        self.logger.debug("Deleting remote file {}".format(self.__file_name))
        try:
            out = self.__ssh.run_command("rm -rf '{}'".format(file_path))
            self.logger.debug("Remote delete output: {}".format(out.decode()))
        except SshError:
            self.logger.exception("Exception while deleting remote file")
