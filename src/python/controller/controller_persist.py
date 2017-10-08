# Copyright 2017, Inderpreet Singh, All rights reserved.

import json

from common import overrides, Persist


class ControllerPersist(Persist):
    """
    Persisting state for controller
    """

    # Keys
    __KEY_DOWNLOADED_FILE_NAMES = "downloaded"

    def __init__(self):
        self.downloaded_file_names = set()

    @classmethod
    @overrides(Persist)
    def from_str(cls: "ControllerPersist", content: str) -> "ControllerPersist":
        persist = ControllerPersist()
        dct = json.loads(content)
        persist.downloaded_file_names = set(dct[ControllerPersist.__KEY_DOWNLOADED_FILE_NAMES])
        return persist

    @overrides(Persist)
    def to_str(self) -> str:
        dct = dict()
        dct[ControllerPersist.__KEY_DOWNLOADED_FILE_NAMES] = list(self.downloaded_file_names)
        return json.dumps(dct)
