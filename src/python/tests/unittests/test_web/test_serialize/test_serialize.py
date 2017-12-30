# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

from web.serialize import Serialize


class DummySerialize(Serialize):
    def dummy(self):
        return self._sse_pack(event="event", data="data")


def parse_stream(serialized_str: str):
    parsed = dict()
    for line in serialized_str.split("\n"):
        if line:
            key, value = line.split(":", maxsplit=1)
            parsed[key.strip()] = value.strip()
    return parsed
