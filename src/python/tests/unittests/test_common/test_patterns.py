# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import os
import tempfile

from common import Patterns, overrides


class TestPatterns(unittest.TestCase):
    def test_patterns(self):
        patterns = Patterns.from_str("Folder.One\nFolder.Two\nFile.One")
        self.assertEqual([
            "Folder.One",
            "Folder.Two",
            "File.One"
        ], patterns.lines)

    def test_patterns_ignore_empty_lines(self):
        patterns = Patterns.from_str("\n\nFolder.One\nFolder.Two\nFile.One\n\n")
        self.assertEqual([
            "Folder.One",
            "Folder.Two",
            "File.One"
        ], patterns.lines)
