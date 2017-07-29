# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

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
