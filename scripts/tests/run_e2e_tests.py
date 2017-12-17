#!/usr/bin/env python3

import argparse
import sys
import os
from subprocess import call
import subprocess
from collections import OrderedDict
import re
from typing import List


# Maps test name to its compose files
TEST_FILES = OrderedDict()
TEST_FILES["pylftp_test_e2e_ubu1604"] = ["compose/e2e-base.yml", "compose/e2e-ubu1604.yml"]
TEST_FILES["pylftp_test_e2e_ubu1704"] = ["compose/e2e-base.yml", "compose/e2e-ubu1704.yml"]


class EndToEndTestsRunner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.realpath(os.path.join(self.script_dir, "..", ".."))
        self.docker_dir = os.path.join(self.root_dir, "src", "docker")

        parser = argparse.ArgumentParser(description="End-to-end tests")
        parser.add_argument("-f", "--deb_file", required=True, help="Path to install deb")
        args = parser.parse_args()

        if not os.path.isfile(args.deb_file):
            sys.exit("Failed to find deb file: {}".format(args.deb_file))
        self.deb_path = os.path.realpath(args.deb_file)

    def run(self):
        self.__setup_environment()
        self.__build()
        self.__run_tests()

    def __setup_environment(self):
        EndToEndTestsRunner.__print_header("Setting up environment")
        os.environ["PATH_TO_INSTALL_DEB"] = self.deb_path
        print("PATH_TO_INSTALL_DEB={}".format(self.deb_path))
        print()

    def __build(self):
        EndToEndTestsRunner.__print_header("Building docker images")

        # Build the pre-requisite images
        call([
            "docker", "build",
            "--rm",
            "-t", "ubuntu-systemd:16.04",
            os.path.join(self.docker_dir, "base", "ubuntu-16.04-systemd")
        ])
        call([
            "docker", "build",
            "--rm",
            "-t", "ubuntu-systemd:17.04",
            os.path.join(self.docker_dir, "base", "ubuntu-17.04-systemd")
        ])

        # Build the test composite images
        for name, files in TEST_FILES.items():
            build_args = [
                "docker-compose",
                *self.__docker_compose_signature(name, files),
                "build"
            ]
            call(build_args)

        print()

    def __run_tests(self):
        EndToEndTestsRunner.__print_header("Running tests")

        passed = True

        for name, files in TEST_FILES.items():
            print("Running test {}".format(name))
            run_args = [
                "docker-compose",
                *self.__docker_compose_signature(name, files),
                "up", "-d", "--force-recreate"
            ]
            call(run_args)

            project_name = re.sub(r'[^a-z0-9]', '', name.lower())
            ret = int(subprocess.check_output(["docker", "wait", "{}_test_1".format(project_name)]))
            passed = passed and ret == 0

            stop_args = [
                "docker-compose",
                *self.__docker_compose_signature(name, files),
                "stop"
            ]
            call(stop_args)

            print("Test {} {}".format(name, "PASSED" if ret == 0 else "FAILED"))
            print()

        print("End-to-end tests: {}".format("PASSED" if passed else "FAILED"))

    def __docker_compose_signature(self, name: str, files: List[str]) -> List[str]:
        args = []
        for file in files:
            args.append("-f")
            args.append(os.path.join(self.docker_dir, file))
        args += ["-p", name]
        return args

    @staticmethod
    def __print_header(header: str):
        print("-------------------------------")
        print(header)
        print("-------------------------------")


if __name__ == "__main__":
    runner = EndToEndTestsRunner()
    runner.run()
