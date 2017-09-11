# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json

from web import Serialize
from model import ModelFile


class TestSerialize(unittest.TestCase):
    @staticmethod
    def __parse(serialized_str: str):
        parsed = dict()
        for line in serialized_str.split("\n"):
            if line:
                key, value = line.split(":", maxsplit=1)
                parsed[key.strip()] = value.strip()
        return parsed

    def test_id_increments(self):
        serialize = Serialize()
        out = TestSerialize.__parse(serialize.model([]))
        idx_new = int(out["id"])
        self.assertGreaterEqual(idx_new, 0)

        idx_old = idx_new
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.ADDED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

        idx_old = idx_new
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.REMOVED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

        idx_old = idx_new
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

    def test_event_names(self):
        serialize = Serialize()
        out = TestSerialize.__parse(serialize.model([]))
        self.assertEqual("init", out["event"])
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.ADDED, None, None
            ))
        )
        self.assertEqual("added", out["event"])
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        self.assertEqual("updated", out["event"])
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.REMOVED, None, None
            ))
        )
        self.assertEqual("removed", out["event"])

    def test_model_is_a_list(self):
        serialize = Serialize()
        files = []
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(list, type(data))

        files = [ModelFile("a", True), ModelFile("b", False)]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(list, type(data))
        self.assertEqual(2, len(data))

    def test_update_event_is_a_dict(self):
        serialize = Serialize()
        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual(dict, type(data))
        self.assertEqual(None, data["old_file"])
        self.assertEqual(None, data["new_file"])

    def test_update_event_files(self):
        serialize = Serialize()
        a1 = ModelFile("a", False)
        a1.local_size = 100
        a2 = ModelFile("a", False)
        a2.local_size = 200

        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.UPDATED, a1, a2
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual("a", data["old_file"]["name"])
        self.assertEqual(100, data["old_file"]["local_size"])
        self.assertEqual("a", data["new_file"]["name"])
        self.assertEqual(200, data["new_file"]["local_size"])

        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.ADDED, None, a1
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual(None, data["old_file"])
        self.assertEqual("a", data["new_file"]["name"])
        self.assertEqual(100, data["new_file"]["local_size"])

        out = TestSerialize.__parse(
            serialize.update_event(Serialize.UpdateEvent(
                Serialize.UpdateEvent.Change.ADDED, a2, None
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual("a", data["old_file"]["name"])
        self.assertEqual(200, data["old_file"]["local_size"])
        self.assertEqual(None, data["new_file"])

    def test_file_name(self):
        serialize = Serialize()
        files = [ModelFile("a", True), ModelFile("b", False)]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(2, len(data))
        self.assertEqual("a", data[0]["name"])
        self.assertEqual("b", data[1]["name"])

    def test_file_is_dir(self):
        serialize = Serialize()
        files = [ModelFile("a", True), ModelFile("b", False)]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(2, len(data))
        self.assertEqual(True, data[0]["is_dir"])
        self.assertEqual(False, data[1]["is_dir"])

    def test_file_state(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        a.state = ModelFile.State.DEFAULT
        b = ModelFile("b", False)
        b.state = ModelFile.State.DOWNLOADING
        c = ModelFile("c", True)
        c.state = ModelFile.State.QUEUED
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual("default", data[0]["state"])
        self.assertEqual("downloading", data[1]["state"])
        self.assertEqual("queued", data[2]["state"])

    def test_remote_size(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        a.remote_size = None
        b = ModelFile("b", False)
        b.remote_size = 0
        c = ModelFile("c", True)
        c.remote_size = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["remote_size"])
        self.assertEqual(0, data[1]["remote_size"])
        self.assertEqual(100, data[2]["remote_size"])

    def test_local_size(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        a.local_size = None
        b = ModelFile("b", False)
        b.local_size = 0
        c = ModelFile("c", True)
        c.local_size = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["local_size"])
        self.assertEqual(0, data[1]["local_size"])
        self.assertEqual(100, data[2]["local_size"])

    def test_downloading_speed(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        a.downloading_speed = None
        b = ModelFile("b", False)
        b.downloading_speed = 0
        c = ModelFile("c", True)
        c.downloading_speed = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["downloading_speed"])
        self.assertEqual(0, data[1]["downloading_speed"])
        self.assertEqual(100, data[2]["downloading_speed"])

    def test_eta(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        a.eta = None
        b = ModelFile("b", False)
        b.eta = 0
        c = ModelFile("c", True)
        c.eta = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["eta"])
        self.assertEqual(0, data[1]["eta"])
        self.assertEqual(100, data[2]["eta"])

    def test_children(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        b = ModelFile("b", True)
        b.add_child(ModelFile("ba", False))
        b.add_child(ModelFile("bb", True))
        c = ModelFile("c", True)
        ca = ModelFile("ca", True)
        ca.add_child(ModelFile("caa", False))
        ca.add_child(ModelFile("cab", False))
        c.add_child(ca)
        cb = ModelFile("cb", False)
        c.add_child(cb)
        c.eta = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(list, type(data[0]["children"]))
        self.assertEqual(0, len(data[0]["children"]))
        self.assertEqual(list, type(data[1]["children"]))
        self.assertEqual(2, len(data[1]["children"]))
        self.assertEqual("ba", data[1]["children"][0]["name"])
        self.assertEqual(0, len(data[1]["children"][0]["children"]))
        self.assertEqual("bb", data[1]["children"][1]["name"])
        self.assertEqual(0, len(data[1]["children"][1]["children"]))
        self.assertEqual(list, type(data[2]["children"]))
        self.assertEqual(2, len(data[2]["children"]))
        self.assertEqual("ca", data[2]["children"][0]["name"])
        self.assertEqual(2, len(data[2]["children"][0]["children"]))
        self.assertEqual("caa", data[2]["children"][0]["children"][0]["name"])
        self.assertEqual(0, len(data[2]["children"][0]["children"][0]["children"]))
        self.assertEqual("cab", data[2]["children"][0]["children"][1]["name"])
        self.assertEqual(0, len(data[2]["children"][0]["children"][1]["children"]))
        self.assertEqual("cb", data[2]["children"][1]["name"])
        self.assertEqual(0, len(data[2]["children"][1]["children"]))

    def test_full_path(self):
        serialize = Serialize()
        a = ModelFile("a", True)
        b = ModelFile("b", True)
        b.add_child(ModelFile("ba", False))
        b.add_child(ModelFile("bb", True))
        c = ModelFile("c", True)
        ca = ModelFile("ca", True)
        ca.add_child(ModelFile("caa", False))
        ca.add_child(ModelFile("cab", False))
        c.add_child(ca)
        cb = ModelFile("cb", False)
        c.add_child(cb)
        c.eta = 100
        files = [a, b, c]
        out = TestSerialize.__parse(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual("a", data[0]["full_path"])
        self.assertEqual("b", data[1]["full_path"])
        self.assertEqual("b/ba", data[1]["children"][0]["full_path"])
        self.assertEqual("b/bb", data[1]["children"][1]["full_path"])
        self.assertEqual("c", data[2]["full_path"])
        self.assertEqual("c/ca", data[2]["children"][0]["full_path"])
        self.assertEqual("c/ca/caa", data[2]["children"][0]["children"][0]["full_path"])
        self.assertEqual("c/ca/cab", data[2]["children"][0]["children"][1]["full_path"])
        self.assertEqual("c/cb", data[2]["children"][1]["full_path"])
