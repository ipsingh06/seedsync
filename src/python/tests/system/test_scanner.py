# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import shutil
import tempfile
import unittest

from system import SystemScanner


# noinspection SpellCheckingInspection
class TestSystemScanner(unittest.TestCase):
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        # Create a temp directory
        TestSystemScanner.temp_dir = tempfile.mkdtemp(prefix="test_system_scanner")

        # Create a bunch files and directories
        # a [dir]
        #   aa [dir]
        #      .aaa [dir]
        #      .aab [file, 512 bytes]
        #   ab [file, 12*1024 + 4 bytes]
        # b [dir]
        #   ba [dir]
        #      baa [file, 512 + 7 bytes]
        #   bb [dir]
        #     bba [dir]
        #     bbb [file, 24*1024*1024 + 24 bytes]
        #     bbc [dir]
        #        bbca [dir]
        #           .bbcaa [file, 1 byte
        # c [file, 1234 bytes]

        def my_mkdir(*args):
            os.mkdir(os.path.join(TestSystemScanner.temp_dir, *args))

        def my_touch(size, *args):
            path = os.path.join(TestSystemScanner.temp_dir, *args)
            with open(path, 'wb') as f:
                f.write(bytearray([0xff]*size))

        my_mkdir("a")
        my_mkdir("a", "aa")
        my_mkdir("a", "aa", ".aaa")
        my_touch(512, "a", "aa", ".aab")
        my_touch(12*1024+4, "a", "ab")
        my_mkdir("b")
        my_mkdir("b", "ba")
        my_touch(512+7, "b", "ba", "baa")
        my_mkdir("b", "bb")
        my_mkdir("b", "bb", "bba")
        my_touch(24*1024*1024+24, "b", "bb", "bbb")
        my_mkdir("b", "bb", "bbc")
        my_mkdir("b", "bb", "bbc", "bbca")
        my_touch(1, "b", "bb", "bbc", "bbca", ".bbcaa")
        my_touch(1234, "c")

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        shutil.rmtree(TestSystemScanner.temp_dir)

    def test_scan_tree(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)

        self.assertEqual("a", a.name)
        self.assertTrue(a.is_dir)
        self.assertEqual("b", b.name)
        self.assertTrue(b.is_dir)
        self.assertEqual("c", c.name)
        self.assertFalse(c.is_dir)

        self.assertEqual(2, len(a.children))
        aa, ab = tuple(a.children)
        self.assertEqual("aa", aa.name)
        self.assertTrue(aa.is_dir)
        self.assertEqual(2, len(aa.children))
        aaa, aab = tuple(aa.children)
        self.assertEqual(".aaa", aaa.name)
        self.assertTrue(aaa.is_dir)
        self.assertEqual(".aab", aab.name)
        self.assertFalse(aab.is_dir)
        self.assertEqual("ab", ab.name)
        self.assertFalse(ab.is_dir)

        self.assertEqual(2, len(b.children))
        ba, bb = tuple(b.children)
        self.assertEqual("ba", ba.name)
        self.assertTrue(ba.is_dir)
        self.assertEqual(1, len(ba.children))
        baa = ba.children[0]
        self.assertEqual("baa", baa.name)
        self.assertFalse(baa.is_dir)
        self.assertEqual("bb", bb.name)
        self.assertTrue(bb.is_dir)
        self.assertEqual(3, len(bb.children))
        bba, bbb, bbc = tuple(bb.children)
        self.assertEqual("bba", bba.name)
        self.assertTrue(bba.is_dir)
        self.assertEqual("bbb", bbb.name)
        self.assertFalse(bbb.is_dir)
        self.assertEqual("bbc", bbc.name)
        self.assertTrue(bbc.is_dir)
        self.assertEqual(1, len(bbc.children))
        bbca = bbc.children[0]
        self.assertEqual("bbca", bbca.name)
        self.assertTrue(bbca.is_dir)
        self.assertEqual(1, len(bbca.children))
        bbcaa = bbca.children[0]
        self.assertEqual(".bbcaa", bbcaa.name)
        self.assertFalse(bbcaa.is_dir)

    def test_scan_size(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        aa, ab = tuple(a.children)
        aaa, aab = tuple(aa.children)
        ba, bb = tuple(b.children)
        baa = ba.children[0]
        bba, bbb, bbc = tuple(bb.children)
        bbca = bbc.children[0]
        bbcaa = bbca.children[0]

        self.assertEqual(12*1024+4+512, a.size)
        self.assertEqual(512, aa.size)
        self.assertEqual(0, aaa.size)
        self.assertEqual(512, aab.size)
        self.assertEqual(12*1024+4, ab.size)
        self.assertEqual(512+7+24*1024*1024+24+1, b.size)
        self.assertEqual(512+7, ba.size)
        self.assertEqual(512+7, baa.size)
        self.assertEqual(24*1024*1024+24+1, bb.size)
        self.assertEqual(0, bba.size)
        self.assertEqual(24*1024*1024+24, bbb.size)
        self.assertEqual(1, bbc.size)
        self.assertEqual(1, bbca.size)
        self.assertEqual(1, bbcaa.size)
        self.assertEqual(1234, c.size)

    def test_scan_tree_excluded_prefix(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        scanner.add_exclude_prefix(".")
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        aa, ab = tuple(a.children)
        ba, bb = tuple(b.children)
        bba, bbb, bbc = tuple(bb.children)
        bbca = bbc.children[0]
        self.assertEqual(0, len(aa.children))
        self.assertEqual(0, len(bbca.children))

        scanner.add_exclude_prefix("ab")
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        self.assertEqual(1, len(a.children))
        aa = a.children[0]
        ba, bb = tuple(b.children)
        bba, bbb, bbc = tuple(bb.children)
        bbca = bbc.children[0]
        self.assertEqual("aa", aa.name)
        self.assertEqual(0, len(bbca.children))

    def test_scan_size_excluded_prefix(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        scanner.add_exclude_prefix(".")
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        aa, ab = tuple(a.children)
        ba, bb = tuple(b.children)
        bba, bbb, bbc = tuple(bb.children)
        bbca = bbc.children[0]
        self.assertEqual(12*1024+4, a.size)
        self.assertEqual(0, aa.size)
        self.assertEqual(24*1024*1024+24+0, bb.size)
        self.assertEqual(0, bbc.size)
        self.assertEqual(0, bbca.size)

        scanner.add_exclude_prefix("ab")
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        self.assertEqual(1, len(a.children))
        aa = a.children[0]
        self.assertEqual("aa", aa.name)
        self.assertEqual(0, a.size)
        self.assertEqual(0, aa.size)

    def test_scan_tree_excluded_suffix(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)

        scanner.add_exclude_suffix("ab")
        scanner.add_exclude_suffix("bb")
        files = scanner.scan()
        self.assertEqual(3, len(files))
        a, b, c = tuple(files)
        self.assertEqual(1, len(a.children))
        aa = a.children[0]
        self.assertEqual("aa", aa.name)
        self.assertEqual(1, len(aa.children))
        aaa = aa.children[0]
        self.assertEqual(".aaa", aaa.name)
        self.assertEqual(1, len(b.children))
        ba = b.children[0]
        self.assertEqual("ba", ba.name)

    def test_scan_size_excluded_suffix(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)

        scanner.add_exclude_suffix("ab")
        scanner.add_exclude_suffix("bb")
        files = scanner.scan()
        a, b, c = tuple(files)
        aa = a.children[0]
        aaa = aa.children[0]
        ba = b.children[0]
        self.assertEqual(0, a.size)
        self.assertEqual(0, aa.size)
        self.assertEqual(0, aaa.size)
        self.assertEqual(512+7, b.size)
        self.assertEqual(512+7, ba.size)
        self.assertEqual(1234, c.size)
