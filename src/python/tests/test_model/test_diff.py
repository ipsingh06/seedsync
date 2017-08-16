# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from datetime import datetime

from model import Model, ModelFile, ModelDiff, ModelDiffUtil


class TestModelDiff(unittest.TestCase):
    def test_change(self):
        diff = ModelDiff(ModelDiff.Change.ADDED, None, None)
        self.assertEqual(ModelDiff.Change.ADDED, diff.change)
        diff = ModelDiff(ModelDiff.Change.REMOVED, None, None)
        self.assertEqual(ModelDiff.Change.REMOVED, diff.change)
        diff = ModelDiff(ModelDiff.Change.UPDATED, None, None)
        self.assertEqual(ModelDiff.Change.UPDATED, diff.change)

    def test_old_file(self):
        old_file = ModelFile("a", False)
        old_file.local_size = 100
        diff = ModelDiff(ModelDiff.Change.ADDED, old_file, None)
        self.assertEqual(old_file, diff.old_file)
        diff = ModelDiff(ModelDiff.Change.ADDED, None, None)
        self.assertEqual(None, diff.old_file)

    def test_new_file(self):
        new_file = ModelFile("a", False)
        new_file.local_size = 100
        diff = ModelDiff(ModelDiff.Change.ADDED, None, new_file)
        self.assertEqual(new_file, diff.new_file)
        diff = ModelDiff(ModelDiff.Change.ADDED, None, None)
        self.assertEqual(None, diff.new_file)


class TestModelDiffUtil(unittest.TestCase):
    def test_added(self):
        model_before = Model()
        model_after = Model()
        a = ModelFile("a", False)
        a.local_size = 100
        model_after.add_file(a)
        diff = ModelDiffUtil.diff_models(model_before, model_after)
        self.assertEqual([ModelDiff(ModelDiff.Change.ADDED, None, a)], diff)

    def test_removed(self):
        model_before = Model()
        model_after = Model()
        a = ModelFile("a", False)
        a.local_size = 100
        model_before.add_file(a)
        diff = ModelDiffUtil.diff_models(model_before, model_after)
        self.assertEqual([ModelDiff(ModelDiff.Change.REMOVED, a, None)], diff)

    def test_updated(self):
        model_before = Model()
        model_after = Model()
        a1 = ModelFile("a", False)
        a1.local_size = 100
        a2 = ModelFile("a", False)
        a2.local_size = 200
        model_before.add_file(a1)
        model_after.add_file(a2)
        diff = ModelDiffUtil.diff_models(model_before, model_after)
        self.assertEqual([ModelDiff(ModelDiff.Change.UPDATED, a1, a2)], diff)

    def test_diff_1(self):
        model_before = Model()
        model_after = Model()
        a = ModelFile("a", False)
        a.local_size = 100
        b = ModelFile("b", False)
        b.remote_size = 200
        c1 = ModelFile("c", False)
        c1.downloading_speed = 40
        c2 = ModelFile("c", False)
        c2.downloading_speed = 50
        d1 = ModelFile("d", False)
        d1.local_size = 500
        d2 = ModelFile("d", False)
        d2.local_size = 500
        d2.update_timestamp = datetime.now()

        # add a, remove b, update c, no change d (but do a timestamp update)
        model_before.add_file(b)
        model_before.add_file(c1)
        model_before.add_file(d1)
        model_after.add_file(a)
        model_after.add_file(c2)
        model_after.add_file(d2)
        diffs = ModelDiffUtil.diff_models(model_before, model_after)

        self.assertEqual(3, len(diffs))
        added = [d for d in diffs if d.change == ModelDiff.Change.ADDED]
        self.assertEqual(1, len(added))
        self.assertEqual(ModelDiff(ModelDiff.Change.ADDED, None, a), added[0])
        removed = [d for d in diffs if d.change == ModelDiff.Change.REMOVED]
        self.assertEqual(1, len(removed))
        self.assertEqual(ModelDiff(ModelDiff.Change.REMOVED, b, None), removed[0])
        updated = [d for d in diffs if d.change == ModelDiff.Change.UPDATED]
        self.assertEqual(1, len(updated))
        self.assertEqual(ModelDiff(ModelDiff.Change.UPDATED, c1, c2), updated[0])
