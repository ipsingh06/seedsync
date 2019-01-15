# Copyright 2017, Inderpreet Singh, All rights reserved.

import os


class TestUtils:
    @staticmethod
    def chmod_from_to(from_path: str, to_path: str, mode: int):
        """
        Chmod from_path and all its parents up to and including to_path
        :param from_path:
        :param to_path:
        :param mode:
        :return:
        """
        path = from_path
        try:
            os.chmod(path, mode)
        except PermissionError:
            pass
        while path != "/" and path != to_path:
            path = os.path.dirname(path)
            try:
                os.chmod(path, mode)
            except PermissionError:
                pass
