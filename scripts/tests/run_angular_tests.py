#!/usr/bin/env python3

import os
from subprocess import call


class EndToEndTestsRunner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.realpath(os.path.join(self.script_dir, "..", ".."))
        self.docker_dir = os.path.join(self.root_dir, "src", "docker")

    def run(self):
        self.__build()
        self.__run_tests()

    def __build(self):
        EndToEndTestsRunner.__print_header("Building docker images")

        call([
            "docker-compose",
            "-f", os.path.join(self.docker_dir, "compose", "angular.yml"),
            "-p", "pylftp_test_angular",
            "build"
        ])

        print()

    def __run_tests(self):
        EndToEndTestsRunner.__print_header("Running tests")
        call([
            "docker-compose",
            "-f", os.path.join(self.docker_dir, "compose", "angular.yml"),
            "-p", "pylftp_test_angular",
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
