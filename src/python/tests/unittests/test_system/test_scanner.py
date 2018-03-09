# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import shutil
import tempfile
import unittest
from threading import Thread

from system import SystemScanner, SystemScannerError


# noinspection SpellCheckingInspection
class TestSystemScanner(unittest.TestCase):
    temp_dir = None

    def setUp(self):
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
                f.write(bytearray([0xff] * size))

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

    def tearDown(self):
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

    def test_scan_non_existing_dir_fails(self):
        scanner = SystemScanner(
            path_to_scan=os.path.join(TestSystemScanner.temp_dir, "nonexisting")
        )
        with self.assertRaises(SystemScannerError) as ex:
            scanner.scan()
        self.assertTrue(str(ex.exception).startswith("Path does not exist"))

    def test_scan_file_fails(self):
        scanner = SystemScanner(
            path_to_scan=os.path.join(TestSystemScanner.temp_dir, "c")
        )
        with self.assertRaises(SystemScannerError) as ex:
            scanner.scan()
        self.assertTrue(str(ex.exception).startswith("Path is not a directory"))

    def test_scan_single_dir(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        a = scanner.scan_single("a")

        self.assertEqual("a", a.name)
        self.assertTrue(a.is_dir)

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

        self.assertEqual(12*1024+4+512, a.size)
        self.assertEqual(512, aa.size)
        self.assertEqual(0, aaa.size)
        self.assertEqual(512, aab.size)
        self.assertEqual(12*1024+4, ab.size)

    def test_scan_single_file(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        c = scanner.scan_single("c")

        self.assertEqual("c", c.name)
        self.assertFalse(c.is_dir)
        self.assertEqual(1234, c.size)

    def test_scan_single_non_existing_path_fails(self):
        scanner = SystemScanner(
            path_to_scan=os.path.join(TestSystemScanner.temp_dir)
        )
        with self.assertRaises(SystemScannerError) as ex:
            scanner.scan_single("nonexisting")
        self.assertTrue(str(ex.exception).startswith("Path does not exist"))

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

    def test_lftp_status_file_size(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)
        size = scanner._lftp_status_file_size("""
        size=243644865
        0.pos=31457280
        0.limit=60911217
        1.pos=87060081
        1.limit=121822433
        2.pos=144268513
        2.limit=182733649
        3.pos=207473489
        3.limit=243644865
        """)
        self.assertEqual(104792064, size)

    def test_scan_lftp_partial_file(self):
        tempdir = tempfile.mkdtemp(prefix="test_system_scanner")

        # Create a partial file
        os.mkdir(os.path.join(tempdir, "t"))
        path = os.path.join(tempdir, "t", "partial.mkv")
        with open(path, 'wb') as f:
            f.write(bytearray([0xff] * 24588))
        # Write the lftp status out
        path = os.path.join(tempdir, "t", "partial.mkv.lftp-pget-status")
        with open(path, "w") as f:
            f.write("""
            size=24588
            0.pos=3157
            0.limit=6147
            1.pos=11578
            1.limit=12294
            2.pos=12295
            2.limit=18441
            3.pos=20000
            3.limit=24588
            """)
        scanner = SystemScanner(tempdir)
        files = scanner.scan()
        self.assertEqual(1, len(files))
        t = files[0]
        self.assertEqual("t", t.name)
        self.assertEqual(10148, t.size)
        self.assertEqual(1, len(t.children))
        partial_mkv = t.children[0]
        self.assertEqual("partial.mkv", partial_mkv.name)
        self.assertEqual(10148, partial_mkv.size)

        # Cleanup
        shutil.rmtree(tempdir)

    def test_scan_single_lftp_partial_file(self):
        # Scan a single partial file
        tempdir = tempfile.mkdtemp(prefix="test_system_scanner")

        # Create a partial file
        path = os.path.join(tempdir, "partial.mkv")
        with open(path, 'wb') as f:
            f.write(bytearray([0xff] * 24588))
        # Write the lftp status out
        path = os.path.join(tempdir, "partial.mkv.lftp-pget-status")
        with open(path, "w") as f:
            f.write("""
            size=24588
            0.pos=3157
            0.limit=6147
            1.pos=11578
            1.limit=12294
            2.pos=12295
            2.limit=18441
            3.pos=20000
            3.limit=24588
            """)
        scanner = SystemScanner(tempdir)
        partial_mkv = scanner.scan_single("partial.mkv")
        self.assertEqual("partial.mkv", partial_mkv.name)
        self.assertEqual(10148, partial_mkv.size)

        # Cleanup
        shutil.rmtree(tempdir)

    def test_scan_lftp_temp_file(self):
        tempdir = tempfile.mkdtemp(prefix="test_system_scanner")

        # Create some temp and non-temp files
        temp1 = os.path.join(tempdir, "a.mkv.lftp")
        with open(temp1, 'wb') as f:
            f.write(bytearray([0xff] * 100))
        temp2 = os.path.join(tempdir, "b.rar.lftp")
        with open(temp2, 'wb') as f:
            f.write(bytearray([0xff] * 200))
        nontemp1 = os.path.join(tempdir, "c.rar")
        with open(nontemp1, 'wb') as f:
            f.write(bytearray([0xff] * 300))
        nontemp2 = os.path.join(tempdir, "d.lftp.avi")
        with open(nontemp2, 'wb') as f:
            f.write(bytearray([0xff] * 400))
        nontemp3 = os.path.join(tempdir, "e")
        os.mkdir(nontemp3)
        temp3 = os.path.join(nontemp3, "ea.txt.lftp")
        with open(temp3, 'wb') as f:
            f.write(bytearray([0xff] * 500))
        nontemp4 = os.path.join(tempdir, "f.lftp")
        os.mkdir(nontemp4)

        scanner = SystemScanner(tempdir)

        # No temp suffix set
        files = scanner.scan()
        self.assertEqual(6, len(files))
        a, b, c, d, e, f = tuple(files)
        self.assertEqual("a.mkv.lftp", a.name)
        self.assertEqual(100, a.size)
        self.assertEqual(False, a.is_dir)
        self.assertEqual("b.rar.lftp", b.name)
        self.assertEqual(200, b.size)
        self.assertEqual(False, b.is_dir)
        self.assertEqual("c.rar", c.name)
        self.assertEqual(300, c.size)
        self.assertEqual(False, c.is_dir)
        self.assertEqual("d.lftp.avi", d.name)
        self.assertEqual(400, d.size)
        self.assertEqual(False, d.is_dir)
        self.assertEqual("e", e.name)
        self.assertEqual(500, e.size)
        self.assertEqual(True, e.is_dir)
        self.assertEqual(1, len(e.children))
        ea = e.children[0]
        self.assertEqual("ea.txt.lftp", ea.name)
        self.assertEqual(500, ea.size)
        self.assertEqual(False, ea.is_dir)
        self.assertEqual("f.lftp", f.name)
        self.assertEqual(0, f.size)
        self.assertEqual(True, f.is_dir)

        # Temp suffix set
        scanner.set_lftp_temp_suffix(".lftp")
        files = scanner.scan()
        self.assertEqual(6, len(files))
        a, b, c, d, e, f = tuple(files)
        self.assertEqual("a.mkv", a.name)
        self.assertEqual(100, a.size)
        self.assertEqual(False, a.is_dir)
        self.assertEqual("b.rar", b.name)
        self.assertEqual(200, b.size)
        self.assertEqual(False, b.is_dir)
        self.assertEqual("c.rar", c.name)
        self.assertEqual(300, c.size)
        self.assertEqual(False, c.is_dir)
        self.assertEqual("d.lftp.avi", d.name)
        self.assertEqual(400, d.size)
        self.assertEqual(False, d.is_dir)
        self.assertEqual("e", e.name)
        self.assertEqual(500, e.size)
        self.assertEqual(True, e.is_dir)
        self.assertEqual(1, len(e.children))
        ea = e.children[0]
        self.assertEqual("ea.txt", ea.name)
        self.assertEqual(500, ea.size)
        self.assertEqual(False, ea.is_dir)
        self.assertEqual("f.lftp", f.name)
        self.assertEqual(0, f.size)
        self.assertEqual(True, f.is_dir)

        # Cleanup
        shutil.rmtree(tempdir)

    def test_scan_single_lftp_temp_file(self):
        tempdir = tempfile.mkdtemp(prefix="test_system_scanner")

        # Create:
        #   temp file
        #   non-temp file and
        #   non-temp directory with temp name
        #   non-temp directory with non-temp name
        temp1 = os.path.join(tempdir, "a.mkv.lftp")
        with open(temp1, 'wb') as f:
            f.write(bytearray([0xff] * 100))

        nontemp1 = os.path.join(tempdir, "b.rar")
        with open(nontemp1, 'wb') as f:
            f.write(bytearray([0xff] * 300))

        nontemp2 = os.path.join(tempdir, "c.lftp")
        os.mkdir(nontemp2)
        temp2 = os.path.join(nontemp2, "c.txt.lftp")
        with open(temp2, 'wb') as f:
            f.write(bytearray([0xff] * 500))

        nontemp3 = os.path.join(tempdir, "d")
        os.mkdir(nontemp3)
        temp3 = os.path.join(nontemp3, "d.avi.lftp")
        with open(temp3, 'wb') as f:
            f.write(bytearray([0xff] * 600))

        scanner = SystemScanner(tempdir)

        # No temp suffix set, must include temp suffix in name param
        file = scanner.scan_single("a.mkv.lftp")
        self.assertEqual("a.mkv.lftp", file.name)
        self.assertEqual(100, file.size)
        self.assertEqual(False, file.is_dir)

        file = scanner.scan_single("b.rar")
        self.assertEqual("b.rar", file.name)
        self.assertEqual(300, file.size)
        self.assertEqual(False, file.is_dir)

        file = scanner.scan_single("c.lftp")
        self.assertEqual("c.lftp", file.name)
        self.assertEqual(500, file.size)
        self.assertEqual(True, file.is_dir)
        self.assertEqual(1, len(file.children))
        child = file.children[0]
        self.assertEqual("c.txt.lftp", child.name)
        self.assertEqual(500, child.size)
        self.assertEqual(False, child.is_dir)

        file = scanner.scan_single("d")
        self.assertEqual("d", file.name)
        self.assertEqual(600, file.size)
        self.assertEqual(True, file.is_dir)
        child = file.children[0]
        self.assertEqual("d.avi.lftp", child.name)
        self.assertEqual(600, child.size)
        self.assertEqual(False, child.is_dir)

        # Temp suffix set, must NOT include temp suffix in name param
        scanner.set_lftp_temp_suffix(".lftp")
        file = scanner.scan_single("a.mkv")
        self.assertEqual("a.mkv", file.name)
        self.assertEqual(100, file.size)
        self.assertEqual(False, file.is_dir)

        file = scanner.scan_single("b.rar")
        self.assertEqual("b.rar", file.name)
        self.assertEqual(300, file.size)
        self.assertEqual(False, file.is_dir)

        file = scanner.scan_single("c.lftp")
        self.assertEqual("c.lftp", file.name)
        self.assertEqual(500, file.size)
        self.assertEqual(True, file.is_dir)
        self.assertEqual(1, len(file.children))
        child = file.children[0]
        self.assertEqual("c.txt", child.name)
        self.assertEqual(500, child.size)
        self.assertEqual(False, child.is_dir)
        # also, shouldn't look for directories with temp suffix
        with self.assertRaises(SystemScannerError) as ctx:
            scanner.scan_single("c")
        self.assertTrue("Path does not exist" in str(ctx.exception))

        file = scanner.scan_single("d")
        self.assertEqual("d", file.name)
        self.assertEqual(600, file.size)
        self.assertEqual(True, file.is_dir)
        child = file.children[0]
        self.assertEqual("d.avi", child.name)
        self.assertEqual(600, child.size)
        self.assertEqual(False, child.is_dir)

        # No file and no temp file
        with self.assertRaises(SystemScannerError) as ctx:
            scanner.scan_single("blah")
        self.assertTrue("Path does not exist" in str(ctx.exception))


        # Cleanup
        shutil.rmtree(tempdir)

    def test_files_deleted_while_scanning(self):
        scanner = SystemScanner(TestSystemScanner.temp_dir)

        stop = False

        # Make and delete files while test runs
        def monkey_with_files():
            orig = os.path.join(TestSystemScanner.temp_dir, "b")
            dest = os.path.join(TestSystemScanner.temp_dir, "b_copy")
            while not stop:
                shutil.copytree(orig, dest)
                shutil.rmtree(dest)
        thread = Thread(target=monkey_with_files)
        thread.start()

        # Scan a bunch of times
        for i in range(0, 2000):
            files = scanner.scan()
            # Must have at least the untouched files
            self.assertGreaterEqual(len(files), 3)
            names = set([f.name for f in files])
            self.assertIn("a", names)
            self.assertIn("b", names)
            self.assertIn("c", names)
        stop = True
        thread.join()
