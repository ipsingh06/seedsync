# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import Optional


class BackendStatus:
    """
    Indicates the status of the backend services
    """
    def __init__(self, up: bool, error_msg: Optional[str]):
        self.up = up
        self.error_msg = error_msg
