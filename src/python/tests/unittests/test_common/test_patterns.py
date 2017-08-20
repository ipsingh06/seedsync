# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile

from common import Patterns, overrides


class TestPatterns(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        # Create empty patterns file
        self.patterns_file = open(tempfile.mktemp(suffix="test_patterns"), "w")

    @overrides(unittest.TestCase)
    def tearDown(self):
        # Remove patterns file
        self.patterns_file.close()
        os.remove(self.patterns_file.name)

    def test_patterns(self):
        self.patterns_file.write("Folder.One\nFolder.Two\nFile.One")
        self.patterns_file.flush()
        patterns = Patterns.from_file(self.patterns_file.name)
        self.assertEqual([
            "Folder.One",
            "Folder.Two",
            "File.One"
        ], patterns.lines)

    def test_patterns_ignore_empty_lines(self):
        self.patterns_file.write("\n\nFolder.One\nFolder.Two\nFile.One\n\n")
        self.patterns_file.flush()
        patterns = Patterns.from_file(self.patterns_file.name)
        self.assertEqual([
            "Folder.One",
            "Folder.Two",
            "File.One"
        ], patterns.lines)
