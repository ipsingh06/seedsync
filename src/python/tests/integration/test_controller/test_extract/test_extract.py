# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import shutil
import tempfile
import os
import subprocess
import zipfile

from common import overrides
from controller.extract import Extract, ExtractError


class TestExtract(unittest.TestCase):
    temp_root = None
    temp_dir = None

    ar_zip = None
    ar_rar = None
    ar_rar_split_p1 = None
    ar_rar_split_p2 = None
    ar_tar_gz = None

    __FILE_CONTENT = "12345678"*10*1024  # 80 KB

    # For debugging
    __KEEP_TMP_FILES = False

    @classmethod
    def setUpClass(cls):
        TestExtract.temp_root = tempfile.mkdtemp(prefix="test_extract_")

        # Create a temp file to archive
        temp_file = os.path.join(TestExtract.temp_root, "file")
        with open(temp_file, "w") as f:
            f.write(TestExtract.__FILE_CONTENT)

        # Create archives
        archive_dir = os.path.join(TestExtract.temp_root, "archives")
        os.mkdir(archive_dir)

        # zip
        TestExtract.ar_zip = os.path.join(archive_dir, "file.zip")
        zf = zipfile.ZipFile(TestExtract.ar_zip, "w", zipfile.ZIP_DEFLATED)
        zf.write(temp_file, os.path.basename(temp_file))
        zf.close()

        # rar
        TestExtract.ar_rar = os.path.join(archive_dir, "file.rar")
        subprocess.Popen(["rar",
                          "a",
                          "-ep",
                          TestExtract.ar_rar,
                          temp_file])

        # rar split
        subprocess.Popen(["rar",
                          "a",
                          "-ep", "-m0", "-v50k",
                          os.path.join(archive_dir, "file.split.rar"),
                          temp_file])
        TestExtract.ar_rar_split_p1 = os.path.join(archive_dir, "file.split.part1.rar")
        TestExtract.ar_rar_split_p2 = os.path.join(archive_dir, "file.split.part2.rar")

        # tar.gz
        TestExtract.ar_tar_gz = os.path.join(archive_dir, "file.tar.gz")
        subprocess.Popen(["tar",
                          "czvf",
                          TestExtract.ar_tar_gz,
                          "-C", os.path.dirname(temp_file),
                          os.path.basename(temp_file)])

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        if not TestExtract.__KEEP_TMP_FILES:
            shutil.rmtree(TestExtract.temp_root)

    @overrides(unittest.TestCase)
    def setUp(self):
        TestExtract.temp_dir = os.path.join(TestExtract.temp_root, "tmp")
        os.mkdir(TestExtract.temp_dir)

    @overrides(unittest.TestCase)
    def tearDown(self):
        if not TestExtract.__KEEP_TMP_FILES:
            shutil.rmtree(TestExtract.temp_dir)

    def _assert_extracted_files(self, dir_path):
        path = os.path.join(dir_path, "file")
        self.assertTrue(os.path.isfile(path))
        with open(path, "r") as f:
            self.assertEqual(TestExtract.__FILE_CONTENT, f.read())

    def test_is_archive_fast(self):
        self.assertTrue(Extract.is_archive_fast("a.zip"))
        self.assertTrue(Extract.is_archive_fast("b.rar"))
        self.assertTrue(Extract.is_archive_fast("c.bz2"))
        self.assertTrue(Extract.is_archive_fast("d.tar.gz"))
        self.assertTrue(Extract.is_archive_fast("e.7z"))

        self.assertFalse(Extract.is_archive_fast("a"))
        self.assertFalse(Extract.is_archive_fast("a.b"))
        self.assertFalse(Extract.is_archive_fast(".b"))
        self.assertFalse(Extract.is_archive_fast(".zip"))
        self.assertFalse(Extract.is_archive_fast(""))
        self.assertFalse(Extract.is_archive_fast("7"))
        self.assertFalse(Extract.is_archive_fast("z"))

    def test_is_archive_fast_works_with_full_paths(self):
        self.assertTrue(Extract.is_archive_fast("/full/path/a.zip"))
        self.assertFalse(Extract.is_archive_fast("/full/path/a"))
        self.assertFalse(Extract.is_archive_fast("/full/path/.zip"))

    def test_is_archive_false_on_nonexisting_file(self):
        self.assertFalse(Extract.is_archive(os.path.join(TestExtract.temp_dir, "no_file")))

    def test_is_archive_false_on_dir(self):
        path = os.path.join(TestExtract.temp_dir, "dir")
        os.mkdir(path)
        self.assertTrue(os.path.isdir(path))
        self.assertFalse(Extract.is_archive(path))

    def test_is_archive_false_on_bad_archive(self):
        path = os.path.join(TestExtract.temp_dir, "bad_file")
        with open(path, 'wb') as f:
            f.write(bytearray(os.urandom(100)))
        self.assertTrue(os.path.isfile(path))
        self.assertFalse(Extract.is_archive(path))

    def test_is_archive_zip(self):
        self.assertTrue(Extract.is_archive(TestExtract.ar_zip))

    def test_is_archive_rar(self):
        self.assertTrue(Extract.is_archive(TestExtract.ar_rar))

    def test_is_archive_rar_split(self):
        self.assertTrue(Extract.is_archive(TestExtract.ar_rar_split_p1))
        self.assertTrue(Extract.is_archive(TestExtract.ar_rar_split_p2))

    def test_is_archive_tar_gz(self):
        self.assertTrue(Extract.is_archive(TestExtract.ar_tar_gz))

    def test_extract_archive_fails_on_nonexisting_file(self):
        with self.assertRaises(ExtractError) as ctx:
            Extract.extract_archive(archive_path=os.path.join(TestExtract.temp_dir, "no_file"),
                                    out_dir_path=TestExtract.temp_dir)
        self.assertTrue(str(ctx.exception).startswith("Path is not a valid archive"))

    def test_extract_archive_fails_on_dir(self):
        with self.assertRaises(ExtractError) as ctx:
            Extract.extract_archive(archive_path=TestExtract.temp_dir,
                                    out_dir_path=TestExtract.temp_dir)
        self.assertTrue(str(ctx.exception).startswith("Path is not a valid archive"))

    def test_extract_archive_fails_on_bad_file(self):
        path = os.path.join(TestExtract.temp_dir, "bad_file")
        with open(path, 'wb') as f:
            f.write(bytearray(os.urandom(100)))
        self.assertTrue(os.path.isfile(path))
        with self.assertRaises(ExtractError) as ctx:
            Extract.extract_archive(archive_path=path,
                                    out_dir_path=TestExtract.temp_dir)
        self.assertTrue(str(ctx.exception).startswith("Path is not a valid archive"))

    def test_extract_archive_creates_sub_directories(self):
        out_path = os.path.join(TestExtract.temp_dir, "bunch", "of", "sub", "dir")
        Extract.extract_archive(archive_path=TestExtract.ar_zip,
                                out_dir_path=out_path)
        self._assert_extracted_files(out_path)

    def test_extract_archive_zip(self):
        Extract.extract_archive(archive_path=TestExtract.ar_zip,
                                out_dir_path=TestExtract.temp_dir)
        self._assert_extracted_files(TestExtract.temp_dir)

    def test_extract_archive_overwrites_existing(self):
        path = os.path.join(TestExtract.temp_dir, "file")
        with open(path, "w") as f:
            f.write("Dummy file")
        Extract.extract_archive(archive_path=TestExtract.ar_zip,
                                out_dir_path=TestExtract.temp_dir)
        self._assert_extracted_files(TestExtract.temp_dir)

    def test_extract_archive_rar(self):
        Extract.extract_archive(archive_path=TestExtract.ar_rar,
                                out_dir_path=TestExtract.temp_dir)
        self._assert_extracted_files(TestExtract.temp_dir)

    def test_extract_archive_rar_split(self):
        Extract.extract_archive(archive_path=TestExtract.ar_rar_split_p1,
                                out_dir_path=TestExtract.temp_dir)
        self._assert_extracted_files(TestExtract.temp_dir)

    def test_extract_archive_tar_gz(self):
        Extract.extract_archive(archive_path=TestExtract.ar_tar_gz,
                                out_dir_path=TestExtract.temp_dir)
        self._assert_extracted_files(TestExtract.temp_dir)
