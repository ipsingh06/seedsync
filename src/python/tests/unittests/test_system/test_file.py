# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from datetime import datetime

from system import SystemFile


class TestSystemFile(unittest.TestCase):
    def test_name(self):
        sf = SystemFile("test", 0, False)
        self.assertEqual("test", sf.name)

    def test_size(self):
        sf = SystemFile("", 42, False)
        self.assertEqual(42, sf.size)
        with self.assertRaises(ValueError) as context:
            # noinspection PyUnusedLocal
            sf = SystemFile("", -42, False)
        self.assertTrue("File size must be greater than zero" in str(context.exception))

    def test_is_dir(self):
        sf = SystemFile("", 0, True)
        self.assertEqual(True, sf.is_dir)
        sf = SystemFile("", 0, False)
        self.assertEqual(False, sf.is_dir)

    def test_time_created(self):
        sf = SystemFile("", 0, True, time_created=datetime(2018, 11, 9, 21, 40, 18))
        self.assertEqual(datetime(2018, 11, 9, 21, 40, 18), sf.timestamp_created)
        sf = SystemFile("", 0, True)
        self.assertIsNone(sf.timestamp_created)

    def test_time_modified(self):
        sf = SystemFile("", 0, True, time_modified=datetime(2018, 11, 9, 21, 40, 18))
        self.assertEqual(datetime(2018, 11, 9, 21, 40, 18), sf.timestamp_modified)
        sf = SystemFile("", 0, True)
        self.assertIsNone(sf.timestamp_modified)

    def test_add_child(self):
        sf = SystemFile("", 0, True)
        sf.add_child(SystemFile("child1", 42, True))
        sf.add_child(SystemFile("child2", 99, False))
        self.assertEqual(2, len(sf.children))
        self.assertEqual("child1", sf.children[0].name)
        self.assertEqual(True, sf.children[0].is_dir)
        self.assertEqual(42, sf.children[0].size)
        self.assertEqual("child2", sf.children[1].name)
        self.assertEqual(False, sf.children[1].is_dir)
        self.assertEqual(99, sf.children[1].size)

    def test_fail_add_child_to_file(self):
        sf = SystemFile("", 0, False)
        with self.assertRaises(TypeError) as context:
            sf.add_child(SystemFile("", 0, False))
        self.assertTrue("Cannot add children to a file" in str(context.exception))

    def test_equality_operator(self):
        a1 = SystemFile("a", 50, is_dir=True,
                        time_created=datetime(2018, 11, 9, 21, 40, 18),
                        time_modified=datetime(2018, 11, 9, 21, 40, 18))
        a1.add_child(SystemFile("aa", 40, is_dir=False))
        a1.add_child(SystemFile("ab", 10, is_dir=False))

        a2 = SystemFile("a", 50, is_dir=True,
                        time_created=datetime(2018, 11, 9, 21, 40, 18),
                        time_modified=datetime(2018, 11, 9, 21, 40, 18))
        a2.add_child(SystemFile("aa", 40, is_dir=False))
        a2.add_child(SystemFile("ab", 10, is_dir=False))

        a3 = SystemFile("a", 50, is_dir=True,
                        time_created=datetime(2018, 11, 9, 21, 40, 18),
                        time_modified=datetime(2018, 11, 9, 21, 40, 18))
        a3.add_child(SystemFile("aa", 40, is_dir=False))
        a3.add_child(SystemFile("ab", 11, is_dir=False))  # different child size

        a4 = SystemFile("a", 50, is_dir=True,
                        time_created=datetime(2018, 11, 9, 21, 40, 19),  # different timestamp
                        time_modified=datetime(2018, 11, 9, 21, 40, 18))
        a4.add_child(SystemFile("aa", 40, is_dir=False))
        a4.add_child(SystemFile("ab", 10, is_dir=False))

        self.assertTrue(a1 == a2)
        self.assertFalse(a1 == a3)
        self.assertFalse(a1 == a4)
