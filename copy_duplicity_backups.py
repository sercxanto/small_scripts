#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" copy_duplicity_backups.py

    Copies most recent duplicity backup files"""

# The MIT License (MIT)
#
# Copyright (c) 2013 Georg Lutz
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
import datetime
import logging
import os
import re
import shutil
import sys


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Copies most recent duplicity backup files")
    parser.add_argument("src", help="Source directory")
    parser.add_argument("dst", help="Destination directory")
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Do not write/delete files. Just print out.")
    parser.add_argument(
        "--maxsize",
        help="Stop copying when dst folder has given size in MB. Default is\
 0 (unlimited)",
        default=0, type=int)
    parser.add_argument(
        "--nr",
        help="Number of full backups (default is 2)",
        default=2, type=int)
    parser.add_argument(
        "--quiet",
        help="If set only errors are printed out",
        action="store_true")

    return parser.parse_args()


class UnknownFileException(Exception):
    '''Exception when we detect a file not belonging to duplicity'''


def ts_regex(number):
    '''Returns timestamp regex, matching group with given number, e.g.
    "timestamp1" or "timestamp2" '''
    if number is not None:
        return "(?P<timestamp" + str(number) + r">\d{8}T\d{2}\d{4}[A-Z])"
    return r"(?P<timestamp>\d{8}T\d{2}\d{4}[A-Z])"


def get_unix_timestamp(timestamp):
    '''Returns a unix timestamp for given textual duplicity timestamp'''
    time = datetime.datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ")
    return (time - datetime.datetime(1970, 1, 1)).total_seconds()


def add_entry(dup_files, timestamp, is_full, filename):
    '''Adds an entry to the dup_files dictionnary.
    Either a new entry with timestamp is created or an existing is updated.

    Example:

        dup_files = {"123456789" :
            { "is_full": True,
              "files": ["file1", "file2", "file3"] } }

    Raises an exception on error'''

    if timestamp in dup_files:
        assert dup_files[timestamp]["is_full"] == is_full
        if "files" in dup_files[timestamp]:
            dup_files[timestamp]["files"].append(filename)
        else:
            dup_files[timestamp]["files"] = [filename]
    else:
        entry = {}
        entry["is_full"] = is_full
        entry["files"] = [filename]
        dup_files[timestamp] = entry


def get_duplicity_files(directory):
    '''For a given directory returns files which belong to duplicity.

    In case that a file is found not belonging to duplicity an exception
    is raised.

       Duplicity naming scheme:
            duplicity-full.timestamp.manifest.gpg
            duplicity-full.timestamp.volnr.difftar.gpg
            duplicity-full-signatures.timestamp.sigtar.gpg
            duplicity-inc.timestamp1.to.timestamp2.manifest.gpg
            duplicity-inc.timestamp1.to.timestamp2.volnr.difftar.gpg
            duplicity-new-signatures.timestamp1.to.timestamp2.sigtar.gpg
       timestamp example: 20130126T070058Z'''

    full_prefix = r"^duplicity\-full\." + ts_regex(None) + r"\."
    full_manifest = re.compile(full_prefix + r"manifest\.gpg$")
    full_difftar = re.compile(full_prefix + r"vol\d+\.difftar\.gpg$")
    full_signatures = re.compile(
        r"^duplicity\-full-signatures\." + ts_regex(None) + r"\.sigtar\.gpg$")
    inc_prefix = r"^duplicity\-inc\." + ts_regex(1) + r"\.to\." + ts_regex(2) + r"\."
    inc_manifest = re.compile(inc_prefix + r"manifest\.gpg$")
    inc_difftar = re.compile(inc_prefix + r"vol\d+\.difftar\.gpg$")
    inc_signatures = re.compile(
        r"^duplicity\-new\-signatures\." + ts_regex(1) + r"\.to\."
        + ts_regex(2) + r"\.sigtar\.gpg$")

    all_files = os.listdir(directory)
    dup_files = {}
    for name in all_files:

        result = full_manifest.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp"))
            add_entry(dup_files, timestamp, True, name)
            continue

        result = full_difftar.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp"))
            add_entry(dup_files, timestamp, True, name)
            continue

        result = full_signatures.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp"))
            add_entry(dup_files, timestamp, True, name)
            continue

        result = inc_manifest.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp2"))
            add_entry(dup_files, timestamp, False, name)
            continue

        result = inc_difftar.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp2"))
            add_entry(dup_files, timestamp, False, name)
            continue

        result = inc_signatures.match(name)
        if result is not None:
            timestamp = get_unix_timestamp(result.group("timestamp2"))
            add_entry(dup_files, timestamp, False, name)
            continue

        raise UnknownFileException(name)
    return dup_files


def return_last_n_full_backups(directory, nr_full):
    '''Returns list of duplicity files for last n full backups into the past

    Args:
        directory: Directory with duplicity backup files
        nr_full: Number of full backups

    Returns:
        list of files without directory prefixed
    '''
    dup_files = get_duplicity_files(directory)
    result = []
    counter = 0
    for key in sorted(iter(dup_files.keys()), reverse=True):
        if counter < nr_full:
            result = result + dup_files[key]["files"]
        else:
            break
        if dup_files[key]["is_full"]:
            counter = counter + 1
    return result


def sync_files(src_dir, dst_dir, files, dryrun, max_size):
    '''Actually copies the files

    The files are copied if they are not existent in dst_dir or if
    the size differs.

    Any existing files in dst_dir not available in files list are deleted!

    Args:
        src_dir: Source directory, where to copy from
        dst_dir: Destination directory, where to copy to
        files: List of filenames without path
        dryrun: If true only simulate and print out message
        max_size: stop with error if dst_dir contains more than max_size bytes.
        If max_size is 0 no limit is enforced.
    Returns:
        1 in case of any error, otherwise 0
    '''

    files_to_delete = []
    files_to_copy = []
    current_size = 0

    dst_files = os.listdir(dst_dir)

    for dst_file in dst_files:
        if dst_file in files:
            dst_size = os.path.getsize(os.path.join(dst_dir, dst_file))
            src_size = os.path.getsize(os.path.join(src_dir, dst_file))
            current_size += src_size
            if dst_size != src_size:
                files_to_delete.append(dst_file)
                files_to_copy.append(dst_file)
        else:
            files_to_delete.append(dst_file)

    for file_ in files:
        if file_ not in dst_files:
            files_to_copy.append(file_)

    for file_ in files_to_delete:
        dst_file = os.path.join(dst_dir, file_)
        if dryrun:
            print(("Would delete " + dst_file))
        else:
            logging.info("Delete %s", dst_file)
            os.unlink(dst_file)

    for file_ in files_to_copy:
        src_file = os.path.join(src_dir, file_)
        dst_file = os.path.join(dst_dir, file_)
        file_size = os.path.getsize(src_file)

        if 0 < max_size < current_size + file_size:
            print("Stopping at " + src_file + " .", file=sys.stderr)
            print((
                "Exceeds file size limit of %d bytes." % (max_size)), file=sys.stderr)
            return 1
        current_size += file_size
        if dryrun:
            print("Would copy " + src_file + " to " + dst_file)
        else:
            logging.info("Copy " + src_file + " to " + dst_file)
            shutil.copyfile(src_file, dst_file)
    return 0


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()

    if args.quiet:
        logging.basicConfig(format="%(message)s", level=logging.WARNING)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)

    if not os.path.isdir(args.src):
        print("Directory \"" + args.src + "\" not found", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.dst):
        print("Directory \"" + args.src + "\" not found", file=sys.stderr)
        sys.exit(1)

    files = return_last_n_full_backups(args.src, args.nr)
    max_size = args.maxsize * 1000000
    return_code = sync_files(args.src, args.dst, files, args.dryrun, max_size)
    sys.exit(return_code)

if __name__ == "__main__":
    main()
