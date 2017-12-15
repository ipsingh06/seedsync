#!/usr/bin/env python3

import argparse
import sys
import os
from subprocess import call
import subprocess
from collections import OrderedDict
import re
from distutils.util import strtobool
from typing import List



class EndToEndTestsRunner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.realpath(os.path.join(self.script_dir, "..", "..", ".."))
        self.docker_dir = os.path.join(self.root_dir, "src", "docker")

    def run(self):
        self.__build()
        self.__run_tests()

    def __build(self):
        EndToEndTestsRunner.__print_header("Building docker images")

        call([
            "docker-compose",
            "-f", os.path.join(self.docker_dir, "compose", "python.yml"),
            "-p", "pylftp_test_python",
            "build"
        ])

        print()

    def __run_tests(self):
        EndToEndTestsRunner.__print_header("Running tests")
        call([
            "docker-compose",
            "-f", os.path.join(self.docker_dir, "compose", "python.yml"),
            "-p", "pylftp_test_python",
            "up", "--force-recreate"
        ])

    @staticmethod
    def __print_header(header: str):
        print("-------------------------------")
        print(header)
        print("-------------------------------")


if __name__ == "__main__":
    runner = EndToEndTestsRunner()
    runner.run()
