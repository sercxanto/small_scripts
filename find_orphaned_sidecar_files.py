#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""find_orphaned_sidecar_files.py

Find sidecar files (like XMP) which don't have the associated base file anymore"""

# The MIT License (MIT)
#
# Copyright (c) 2021 Georg Lutz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Standard library imports:
import argparse
import os
import logging
import sys
from typing import List, Generator


# list of file extensions, all lowercase, without leading "."
DEFAULT_SIDECAR_EXTENSIONS = [
    "xmp",
    "pp3"
]

def get_args(args):
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="""Find sidecar files (like XMP) which don't
        have the associated base file anymore""")
    parser.add_argument(
        "base_folder",
        help="Base folder to recursively search for orphaned sidecar files")
    parser.add_argument(
        "-d", "--debug", dest="debuglevel", action="store_const",
        const=logging.DEBUG, default=logging.INFO,
        help="Enables verbose/debug output")
    parser.add_argument(
        "-e", "--extensions", type=lambda x: x.lower().split(","),
        default=DEFAULT_SIDECAR_EXTENSIONS,
        help="Comma seperated list of sidecar file extensions. Defaults to \"{}\"".format(
            ",".join(DEFAULT_SIDECAR_EXTENSIONS)))
    return parser.parse_args(args)


def get_orphaned_files(files_in_folder: List[str], sidecar_extensions: List[str]) -> List[str]:
    '''Returns orphaned files from a specific folder

    In the following example both abc.def.xyz and abc.def are considered as sidecar
    files for abc.def:

    abc.def
    abc.def.xyz
    abc.xyz

    Arguments:

    files_in_folder: List of filenames in folders
    sidecar_extensions: List of sidecar file extensions

    Returns:

    List of orphaned files
    '''

    result = []
    sidecar_files = [] # list of sidecar only files
    orig_files_base = [] # original file names, no sidecar files

    for entry in files_in_folder:
        base, ext = os.path.splitext(entry)
        if ext.lower().lstrip(".") in sidecar_extensions:
            sidecar_files.append(entry)
        else:
            # Match for abc.def
            orig_files_base.append(entry)
            # Match for abc.xyz
            orig_files_base.append(base)

    for entry in sidecar_files:
        base, ext = os.path.splitext(entry)
        if not base in orig_files_base:
            result.append(entry)

    return result


def find_files(base_folder: str, sidecar_extensions) -> Generator[str, None, None]:
    '''Find sidecar files

    Arguments:

    base_folder: The base folder where to start the recursive search
    sidecar_extensions: List of sidecar file extensions

    Returns a list of duplicates (yield)
    '''

    for root, _, files in os.walk(base_folder, followlinks=True):
        if files:
            logging.debug("Checking %s with %d files", root, len(files))
            orphaned_files = get_orphaned_files(files, sidecar_extensions)
            if orphaned_files:
                for file_ in orphaned_files:
                    yield os.path.join(root, file_)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args(sys.argv[1:])
    logging.basicConfig(format="%(message)s", level=args.debuglevel)
    for entry in find_files(args.base_folder, args.extensions):
        print(entry)


if __name__ == "__main__":
    main()
