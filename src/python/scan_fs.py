# Copyright 2017, Inderpreet Singh, All rights reserved.

import pickle
import sys
import argparse

# my libs
from system import SystemScanner, SystemFile, SystemScannerError


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    parser = argparse.ArgumentParser(description="File size scanner")
    parser.add_argument("path", help="Path of the root directory to scan")
    parser.add_argument("-e", "--exclude-hidden", action="store_true", default=False,
                        help="Exclude hidden files")
    parser.add_argument("-H", "--human-readable", action="store_true", default=False,
                        help="Human readable output")
    args = parser.parse_args()

    scanner = SystemScanner(args.path)
    if args.exclude_hidden:
        scanner.add_exclude_prefix(".")
    try:
        root_files = scanner.scan()
    except SystemScannerError as e:
        sys.exit("SystemScannerError: {}".format(str(e)))
    if args.human_readable:
        def print_file(file: SystemFile, level: int):
            sys.stdout.write("  "*level)
            sys.stdout.write("{} {} {}\n".format(
                file.name,
                "d" if file.is_dir else "f",
                file.size
            ))
            for child in file.children:
                print_file(child, level+1)
        for root_file in root_files:
            print_file(root_file, 0)
    else:
        bytes_out = pickle.dumps(root_files)
        sys.stdout.buffer.write(bytes_out)
