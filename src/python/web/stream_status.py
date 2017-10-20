# Copyright 2017, Inderpreet Singh, All rights reserved.

from typing import Optional

from .web_app_stream import WebAppStream
from .serialize import SerializeBackendStatus
from .utils import StreamQueue
from .status import BackendStatus, IBackendStatusListener, IBackendStatusProvider
from common import overrides


class BackendStatusListener(IBackendStatusListener, StreamQueue[BackendStatus]):
    """
    Status listener used by status streams to listen to status updates
    """
    def __init__(self):
        super().__init__()

    @overrides(IBackendStatusListener)
    def notify(self, status: BackendStatus):
        self.put(status)


class StreamStatus(WebAppStream):
    _EVENT_BLOCK_INTERVAL_IN_MS = 500

    def __init__(self, status_provider: IBackendStatusProvider):
        self.status_provider = status_provider
        self.serialize = SerializeBackendStatus()
        self.status_listener = BackendStatusListener()
        self.first_run = True

    @overrides(WebAppStream)
    def setup(self):
        self.status_provider.add_listener(self.status_listener)

    @overrides(WebAppStream)
    def get_value(self) -> Optional[str]:
        if self.first_run:
            self.first_run = False
            return self.serialize.status(self.status_provider.get_status())
        else:
            status = self.status_listener.get_next_event(timeout_in_ms=StreamStatus._EVENT_BLOCK_INTERVAL_IN_MS)
            if status:
                return self.serialize.status(status)
            else:
                return None

    @overrides(WebAppStream)
    def cleanup(self):
        if self.status_listener:
            self.status_provider.remove_listener(self.status_listener)
