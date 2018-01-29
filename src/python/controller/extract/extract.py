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
    def is_archive(archive_path: str) -> bool:
        if not os.path.isfile(archive_path):
            return False
        try:
            # noinspection PyUnusedLocal,PyShadowingBuiltins
            format, compression = patoolib.get_archive_format(archive_path)
            return True
        except patoolib.util.PatoolError:
            return False

    @staticmethod
    def is_archive_fast(archive_path: str) -> bool:
        """
        Fast version of is_archive that only looks at file extension
        May return false negatives
        :param archive_path:
        :return:
        """
        file_ext = os.path.splitext(os.path.basename(archive_path))[1]
        if file_ext:
            file_ext = file_ext[1:]  # remove the dot
            # noinspection SpellCheckingInspection
            return file_ext in [
                "7z",
                "bz2",
                "gz",
                "lz",
                "rar",
                "tar", "tgz", "tbz2",
                "zip", "zipx"
            ]
        else:
            return False

    @staticmethod
    def extract_archive(archive_path: str, out_dir_path: str):
        if not Extract.is_archive(archive_path):
            raise ExtractError("Path is not a valid archive: {}".format(archive_path))
        try:
            # Try to create the outdir path
            if not os.path.exists(out_dir_path):
                os.makedirs(out_dir_path)
            patoolib.extract_archive(archive_path, outdir=out_dir_path, interactive=False)
        except FileNotFoundError as e:
            raise ExtractError(str(e))
        except patoolib.util.PatoolError as e:
            raise ExtractError(str(e))
