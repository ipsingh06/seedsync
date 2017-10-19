# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import json

from web import SerializeModel, SerializeBackendStatus, BackendStatus
from model import ModelFile


def parse_stream(serialized_str: str):
    parsed = dict()
    for line in serialized_str.split("\n"):
        if line:
            key, value = line.split(":", maxsplit=1)
            parsed[key.strip()] = value.strip()
    return parsed


class TestSerializeStatus(unittest.TestCase):
    def test_id_increments(self):
        serialize = SerializeBackendStatus()
        out = parse_stream(serialize.status(BackendStatus(True, None)))
        idx_new = int(out["id"])
        self.assertGreaterEqual(idx_new, 0)

        idx_old = idx_new
        out = parse_stream(serialize.status(BackendStatus(False, "Bad stuff happened")))
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

    def test_event_names(self):
        serialize = SerializeBackendStatus()
        out = parse_stream(serialize.status(BackendStatus(True, None)))
        self.assertEqual("status", out["event"])

        out = parse_stream(serialize.status(BackendStatus(False, "Bad stuff happened")))
        self.assertEqual("status", out["event"])

    def test_status_up(self):
        serialize = SerializeBackendStatus()
        out = parse_stream(serialize.status(BackendStatus(True, None)))
        data = json.loads(out["data"])
        self.assertEqual(True, data["up"])

        out = parse_stream(serialize.status(BackendStatus(False, "Bad stuff happened")))
        data = json.loads(out["data"])
        self.assertEqual(False, data["up"])

    def test_status_error_msg(self):
        serialize = SerializeBackendStatus()
        out = parse_stream(serialize.status(BackendStatus(True, None)))
        data = json.loads(out["data"])
        self.assertEqual(None, data["error_msg"])

        out = parse_stream(serialize.status(BackendStatus(False, "Bad stuff happened")))
        data = json.loads(out["data"])
        self.assertEqual("Bad stuff happened", data["error_msg"])


class TestSerializeModel(unittest.TestCase):
    def test_id_increments(self):
        serialize = SerializeModel()
        out = parse_stream(serialize.model([]))
        idx_new = int(out["id"])
        self.assertGreaterEqual(idx_new, 0)

        idx_old = idx_new
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.ADDED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

        idx_old = idx_new
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.REMOVED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

        idx_old = idx_new
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        idx_new = int(out["id"])
        self.assertGreater(idx_new, idx_old)

    def test_event_names(self):
        serialize = SerializeModel()
        out = parse_stream(serialize.model([]))
        self.assertEqual("init", out["event"])
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.ADDED, None, None
            ))
        )
        self.assertEqual("added", out["event"])
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        self.assertEqual("updated", out["event"])
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.REMOVED, None, None
            ))
        )
        self.assertEqual("removed", out["event"])

    def test_model_is_a_list(self):
        serialize = SerializeModel()
        files = []
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(list, type(data))

        files = [ModelFile("a", True), ModelFile("b", False)]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(list, type(data))
        self.assertEqual(2, len(data))

    def test_update_event_is_a_dict(self):
        serialize = SerializeModel()
        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.UPDATED, None, None
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual(dict, type(data))
        self.assertEqual(None, data["old_file"])
        self.assertEqual(None, data["new_file"])

    def test_update_event_files(self):
        serialize = SerializeModel()
        a1 = ModelFile("a", False)
        a1.local_size = 100
        a2 = ModelFile("a", False)
        a2.local_size = 200

        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.UPDATED, a1, a2
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual("a", data["old_file"]["name"])
        self.assertEqual(100, data["old_file"]["local_size"])
        self.assertEqual("a", data["new_file"]["name"])
        self.assertEqual(200, data["new_file"]["local_size"])

        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.ADDED, None, a1
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual(None, data["old_file"])
        self.assertEqual("a", data["new_file"]["name"])
        self.assertEqual(100, data["new_file"]["local_size"])

        out = parse_stream(
            serialize.update_event(SerializeModel.UpdateEvent(
                SerializeModel.UpdateEvent.Change.ADDED, a2, None
            ))
        )
        data = json.loads(out["data"])
        self.assertEqual("a", data["old_file"]["name"])
        self.assertEqual(200, data["old_file"]["local_size"])
        self.assertEqual(None, data["new_file"])

    def test_file_name(self):
        serialize = SerializeModel()
        files = [ModelFile("a", True), ModelFile("b", False)]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(2, len(data))
        self.assertEqual("a", data[0]["name"])
        self.assertEqual("b", data[1]["name"])

    def test_file_is_dir(self):
        serialize = SerializeModel()
        files = [ModelFile("a", True), ModelFile("b", False)]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(2, len(data))
        self.assertEqual(True, data[0]["is_dir"])
        self.assertEqual(False, data[1]["is_dir"])

    def test_file_state(self):
        serialize = SerializeModel()
        a = ModelFile("a", True)
        a.state = ModelFile.State.DEFAULT
        b = ModelFile("b", False)
        b.state = ModelFile.State.DOWNLOADING
        c = ModelFile("c", True)
        c.state = ModelFile.State.QUEUED
        d = ModelFile("d", True)
        d.state = ModelFile.State.DOWNLOADED
        e = ModelFile("e", False)
        e.state = ModelFile.State.DELETED
        files = [a, b, c, d, e]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(5, len(data))
        self.assertEqual("default", data[0]["state"])
        self.assertEqual("downloading", data[1]["state"])
        self.assertEqual("queued", data[2]["state"])
        self.assertEqual("downloaded", data[3]["state"])
        self.assertEqual("deleted", data[4]["state"])

    def test_remote_size(self):
        serialize = SerializeModel()
        a = ModelFile("a", True)
        a.remote_size = None
        b = ModelFile("b", False)
        b.remote_size = 0
        c = ModelFile("c", True)
        c.remote_size = 100
        files = [a, b, c]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["remote_size"])
        self.assertEqual(0, data[1]["remote_size"])
        self.assertEqual(100, data[2]["remote_size"])

    def test_local_size(self):
        serialize = SerializeModel()
        a = ModelFile("a", True)
        a.local_size = None
        b = ModelFile("b", False)
        b.local_size = 0
        c = ModelFile("c", True)
        c.local_size = 100
        files = [a, b, c]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["local_size"])
        self.assertEqual(0, data[1]["local_size"])
        self.assertEqual(100, data[2]["local_size"])

    def test_downloading_speed(self):
        serialize = SerializeModel()
        a = ModelFile("a", True)
        a.downloading_speed = None
        b = ModelFile("b", False)
        b.downloading_speed = 0
        c = ModelFile("c", True)
        c.downloading_speed = 100
        files = [a, b, c]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["downloading_speed"])
        self.assertEqual(0, data[1]["downloading_speed"])
        self.assertEqual(100, data[2]["downloading_speed"])

    def test_eta(self):
        serialize = SerializeModel()
        a = ModelFile("a", True)
        a.eta = None
        b = ModelFile("b", False)
        b.eta = 0
        c = ModelFile("c", True)
        c.eta = 100
        files = [a, b, c]
        out = parse_stream(serialize.model(files))
        data = json.loads(out["data"])
        self.assertEqual(3, len(data))
        self.assertEqual(None, data[0]["eta"])
        self.assertEqual(0, data[1]["eta"])
        self.assertEqual(100, data[2]["eta"])

    def test_children(self):
        serialize = SerializeModel()
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
        out = parse_stream(serialize.model(files))
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
        serialize = SerializeModel()
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
        out = parse_stream(serialize.model(files))
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
