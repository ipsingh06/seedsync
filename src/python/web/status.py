# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import Optional
from abc import ABC, abstractmethod


class BackendStatus:
    """
    Indicates the status of the backend services
    """
    def __init__(self, up: bool, error_msg: Optional[str]):
        self.up = up
        self.error_msg = error_msg


class IBackendStatusListener(ABC):
    @abstractmethod
    def notify(self, status: BackendStatus):
        pass


class IBackendStatusProvider(ABC):
    @abstractmethod
    def add_listener(self, listener: IBackendStatusListener):
        pass

    @abstractmethod
    def remove_listener(self, listener: IBackendStatusListener):
        pass

    @abstractmethod
    def get_status(self) -> BackendStatus:
        pass
