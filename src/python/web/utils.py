# Copyright 2017, Inderpreet Singh, All rights reserved.

from queue import Queue, Empty
from typing import TypeVar, Generic, Optional


T = TypeVar('T')


class StreamQueue(Generic[T]):
    """
    A queue that transfers events from one thread to another.
    Useful for web streams that wait for listener events from other threads.
    The producer thread calls put() to insert events. The consumer stream
    calls get_next_event() to receive event in its own thread.
    """
    def __init__(self):
        self.__queue = Queue()

    def put(self, event: T):
        self.__queue.put(event)

    def get_next_event(self, timeout_in_ms: int) -> Optional[T]:
        """
        Returns the next event, or blocks for the specified timeout until an event is available.
        Returns None if timeout expires and no event is available
        :return:
        """
        try:
            return self.__queue.get(block=True, timeout=float(timeout_in_ms)/1000)
        except Empty:
            return None
