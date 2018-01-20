# Copyright 2017, Inderpreet Singh, All rights reserved.

import os

import patoolib
import patoolib.util

from common import AppError


class ExtractError(AppError):
    """
    Indicates an extraction error
    """
    pass


class Extract:
    """
    Utility to extract archive files
    """
    @staticmethod
    def is_archive(archive_path: str):
        if not os.path.isfile(archive_path):
            return False
        try:
            # noinspection PyUnusedLocal,PyShadowingBuiltins
            format, compression = patoolib.get_archive_format(archive_path)
            return True
        except patoolib.util.PatoolError:
            return False

    @staticmethod
    def extract_archive(archive_path: str, out_dir_path: str):
        if not Extract.is_archive(archive_path):
            raise ExtractError("Path is not a valid archive: {}".format(archive_path))
        try:
            patoolib.extract_archive(archive_path, outdir=out_dir_path, interactive=False)
        except patoolib.util.PatoolError as e:
            raise ExtractError(str(e))
