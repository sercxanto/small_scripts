#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" Unittests for copy_duplicity_backups """

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

# Standard library imports
import datetime
import filecmp
import os
import random
import shutil
import sys
import unittest
import tempfile

TESTSCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)

# Module to test
import copy_duplicity_backups # pylint: disable=import-error,wrong-import-position


# pylint: disable=too-few-public-methods
class TestNameGenerator(object):
    '''Helper class for tests
    Generates names for files'''

    def __init__(self):
        self.last_timestamp_object = None

    # pylint: disable=too-many-arguments
    def gen_names(self, inc_full, year, month, day, nr_vols):
        '''Generates a list of file names for a backup run

        For incremental backups the first timestamp is automatically
        set to the last backup.

        Args:
            inc_full: Either "full" or "inc"
            year: numerical year of backup
            month: numerical month of backup
            nr_vols: number of volumes

        Returns:
            list of Strings.
            '''
        datetime_format = "%Y%m%dT%H%M%SZ"
        assert inc_full == "inc" or inc_full == "full"

        timestamp_object = datetime.datetime(year, month, day)
        timestamp = timestamp_object.strftime(datetime_format)
        manifest = ""
        signatures = ""
        vols = []

        if inc_full == "full":
            manifest = "duplicity-full." + timestamp + ".manifest.gpg"
            signatures = ("duplicity-full-signatures.%s.sigtar.gpg" % (timestamp))
            for i in range(1, nr_vols + 1):
                vols.append("duplicity-full.%s.vol%d.difftar.gpg" % (timestamp, i))
        else:
            last_timestamp = (
                self.last_timestamp_object.strftime(datetime_format))
            manifest = ("duplicity-inc.%s.to.%s.manifest.gpg" %
                        (last_timestamp, timestamp))
            signatures = ("duplicity-new-signatures.%s.to.%s.sigtar.gpg" %
                          (last_timestamp, timestamp))
            for i in range(1, nr_vols + 1):
                vols.append(
                    "duplicity-inc.%s.to.%s.vol%d.difftar.gpg" %
                    (last_timestamp, timestamp, i))

        self.last_timestamp_object = timestamp_object
        result = vols
        result.append(signatures)
        result.append(manifest)
        return result


class TestReturnBackups(unittest.TestCase):
    '''Test for return_last_n_full_backups'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(
            prefix="tmp_copy_duplicity_backups_return_backups")

    @staticmethod
    def add_files(folder, filenames):
        '''Adds an empty filename to folder '''
        for filename in filenames:
            path = os.path.join(folder, filename)
            with open(path, mode="wb"):
                pass



    def test_01(self):
        '''Only one full'''
        folder = self.gen_tempfolder()
        names_in = [
            "duplicity-full.20130101T010000Z.manifest.gpg",
            "duplicity-full.20130101T010000Z.vol1.difftar.gpg",
            "duplicity-full.20130101T010000Z.vol2.difftar.gpg",
            "duplicity-full-signatures.20130101T010000Z.sigtar.gpg"
            ]
        self.add_files(folder, names_in)
        result = copy_duplicity_backups.return_last_n_full_backups(folder, 3)
        self.assertEqual(sorted(names_in), sorted(result))

        shutil.rmtree(folder)

    def test_02(self):
        '''One full and old incs from previous backup'''
        folder = self.gen_tempfolder()
        old_leftover = [
            "duplicity-inc.20130101T000000Z.to.20130101T000001Z.manifest.gpg",
            "duplicity-inc.20130101T000000Z.to.20130101T000001Z.vol1.difftar.gpg",
            "duplicity-new-signatures.20130101T010000Z.to.20130101T000001Z.sigtar.gpg"
            ]
        last_full = [
            "duplicity-full.20130101T010000Z.manifest.gpg",
            "duplicity-full.20130101T010000Z.vol1.difftar.gpg",
            "duplicity-full.20130101T010000Z.vol2.difftar.gpg",
            "duplicity-full-signatures.20130101T010000Z.sigtar.gpg"
            ]
        names_in = old_leftover + last_full
        self.add_files(folder, names_in)

        result = copy_duplicity_backups.return_last_n_full_backups(folder, 1)
        self.assertEqual(sorted(last_full), sorted(result))

        shutil.rmtree(folder)

    def test_03(self):
        '''Full with incs and one old inc'''
        folder = self.gen_tempfolder()
        old_leftover = [
            "duplicity-inc.20130101T000000Z.to.20130101T000001Z.manifest.gpg",
            "duplicity-inc.20130101T000000Z.to.20130101T000001Z.vol1.difftar.gpg",
            "duplicity-new-signatures.20130101T010000Z.to.20130101T000001Z.sigtar.gpg"
            ]
        last_full = [
            "duplicity-full.20130101T010000Z.manifest.gpg",
            "duplicity-full.20130101T010000Z.vol1.difftar.gpg",
            "duplicity-full.20130101T010000Z.vol2.difftar.gpg",
            "duplicity-full-signatures.20130101T010000Z.sigtar.gpg"
            ]
        after_full = [
            "duplicity-inc.20130101T010000Z.to.20130102T010001Z.manifest.gpg",
            "duplicity-inc.20130101T010000Z.to.20130102T010001Z.vol1.difftar.gpg",
            "duplicity-new-signatures.20130101T010000Z.to.20130102T010001Z.sigtar.gpg",
            "duplicity-inc.20130102T010001Z.to.20130103T010000Z.manifest.gpg",
            "duplicity-inc.20130102T010001Z.to.20130103T010000Z.vol1.difftar.gpg",
            "duplicity-new-signatures.20130102T010001Z.to.20130103T010000Z.sigtar.gpg"
            ]
        names_in = old_leftover + last_full + after_full
        self.add_files(folder, names_in)

        result = copy_duplicity_backups.return_last_n_full_backups(folder, 1)
        self.assertEqual(sorted(last_full+after_full), sorted(result))

        shutil.rmtree(folder)


    def test_04(self):
        '''3 fulls with incs, select last 2 fulls'''

        gen = TestNameGenerator()

        full_1 = gen.gen_names("full", 2013, 1, 1, 8)
        incs_1 = (
            gen.gen_names("inc", 2013, 1, 2, 1) +
            gen.gen_names("inc", 2013, 1, 3, 1) +
            gen.gen_names("inc", 2013, 1, 4, 2) +
            gen.gen_names("inc", 2013, 1, 6, 1))

        full_2 = gen.gen_names("full", 2013, 1, 8, 1)
        incs_2 = (
            gen.gen_names("inc", 2013, 1, 9, 3) +
            gen.gen_names("inc", 2013, 1, 10, 4) +
            gen.gen_names("inc", 2013, 1, 11, 2))

        full_3 = gen.gen_names("full", 2013, 2, 1, 1)
        incs_3 = (
            gen.gen_names("inc", 2013, 2, 3, 2) +
            gen.gen_names("inc", 2013, 2, 4, 20))


        names_in = full_1 + incs_1 + full_2 + incs_2 + full_3 + incs_3

        folder = self.gen_tempfolder()
        self.add_files(folder, names_in)

        result = copy_duplicity_backups.return_last_n_full_backups(folder, 2)
        expected = full_2 + incs_2 + full_3 + incs_3

        self.assertEqual(sorted(result), sorted(expected))

        shutil.rmtree(folder)


    def test_05(self):
        '''Multi regex match'''
        folder = self.gen_tempfolder()
        # Multiple matches for a wrong file,
        # "^" / "$"  in regex necessary
        names_in = [
            "duplicity-full.20130101T010000Z.manifest.gpg",
            "duplicity-full.20130101T010000Z.vol1.difftar.gpg"
            "duplicity-full.20130101T010000Z.vol2.difftar.gpg"
            "duplicity-full-signatures.20130101T010000Z.sigtar.gpg"
            ]

        self.add_files(folder, names_in)

        with self.assertRaises(copy_duplicity_backups.UnknownFileException):
            copy_duplicity_backups.return_last_n_full_backups(folder, 3)

        shutil.rmtree(folder)


def gen_random_files(rnd, folder, nr_files):
    '''Generates a number of files with random name and content

    The file length is equaly distributed between 1 and 10000 bytes.
    The names are numbered testfile_0000, testfile_0001 etc.
    A random object has to be provided. Seed it before to create reproducable
    tests (at leat between different runs).

    Args:
        rnd: Random object from standard library.
        folder: The folder where to create the random files
        nr_files: The number of files to create
    Return:
        List of filenames without folder name prefixed
    '''
    result = []

    for i in range(nr_files):
        filename = "test_%04d" % (i)
        result.append(filename)
        size = rnd.randint(1, 10000)
        with open(os.path.join(folder, filename), mode="wb") as file_:
            j = 0
            while j < size:
                file_.write(bytearray([rnd.randint(0, 255)]))
                j = j + 1
    return result


def gen_dummy_file(file_path, nr_bytes):
    '''Write nr_bytes dummy data to file.

    An existing file will be overwritten.

    Args:
        file_path: Complete path to the file (folder + file name).
        nr_bytes: Number of bytes write to that files.

    Return:
        This function does not return anything.'''

    with open(file_path, mode="wb") as file_:
        for i in range(0, nr_bytes):
            file_.write(bytearray([i % 255]))


def cmp_src_dst_files(src_dir, dst_dir, filelist):
    '''Checks if files in filelist are available at dst_dir
    and are equal to src_dir

    Args:
        src_dir: Source directory
        dst_dir: Destination directory
        filelist: List of files to be compared

    Returns:
        True if dst_dir contains only files in filelist and if the file content
        is equal to thise in src_dir. Otherwise false.'''

    dst_files = sorted(os.listdir(dst_dir))

    if dst_files != sorted(filelist):
        return False

    for file_ in filelist:
        src_file = os.path.join(src_dir, file_)
        dst_file = os.path.join(dst_dir, file_)
        if not filecmp.cmp(src_file, dst_file, shallow=False):
            return False

    return True


class TestSyncFiles(unittest.TestCase):
    '''Test for sync_files'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_copy_duplicity_backups_sync_files")

    def test_01(self):
        '''Empty folders, empty list'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        copy_duplicity_backups.sync_files(src_dir, dst_dir, [], False, 0)
        self.assertEqual(len(os.listdir(dst_dir)), 0)

        shutil.rmtree(folder)

    def test_02(self):
        '''Empty source folder, file present in dst, list empty'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        with open(os.path.join(dst_dir, "empty_file"), mode="wb"):
            pass

        copy_duplicity_backups.sync_files(src_dir, dst_dir, [], False, 0)
        self.assertEqual(len(os.listdir(dst_dir)), 0)

        shutil.rmtree(folder)

    def test_03(self):
        '''Same file in source and destination, list empty'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        with open(os.path.join(src_dir, "empty_file"), mode="wb"):
            pass
        with open(os.path.join(dst_dir, "empty_file"), mode="wb"):
            pass

        copy_duplicity_backups.sync_files(src_dir, dst_dir, [], False, 0)
        self.assertEqual(len(os.listdir(dst_dir)), 0)

        shutil.rmtree(folder)

    def test_04(self):
        '''Same file in source, destination and list'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        with open(os.path.join(src_dir, "empty_file"), mode="wb"):
            pass
        with open(os.path.join(dst_dir, "empty_file"), mode="wb"):
            pass

        copy_duplicity_backups.sync_files(
            src_dir, dst_dir, ["empty_file"],
            False, 0)
        dst_files = os.listdir(dst_dir)
        self.assertEqual(len(dst_files), 1)
        self.assertIn("empty_file", dst_files)

        shutil.rmtree(folder)

    def test_05(self):
        '''Same two files in source and destination, list only one file'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        with open(os.path.join(src_dir, "empty_file1"), mode="wb"):
            pass
        with open(os.path.join(src_dir, "empty_file2"), mode="wb"):
            pass
        with open(os.path.join(dst_dir, "empty_file1"), mode="wb"):
            pass
        with open(os.path.join(dst_dir, "empty_file2"), mode="wb"):
            pass

        copy_duplicity_backups.sync_files(
            src_dir, dst_dir, ["empty_file1"],
            False, 0)
        dst_files = os.listdir(dst_dir)
        self.assertEqual(len(dst_files), 1)
        self.assertIn("empty_file1", dst_files)

        shutil.rmtree(folder)

    def test_06(self):
        '''Same two files in source and destination, both in list,
        one differs in size'''

        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        with open(os.path.join(src_dir, "nonempty_file"), mode="w") as file_:
            file_.write("new content")
        with open(os.path.join(src_dir, "empty_file"), mode="w"):
            pass
        with open(os.path.join(dst_dir, "nonempty_file"), mode="w") as file_:
            file_.write("old content, old size")
        with open(os.path.join(dst_dir, "empty_file"), mode="w"):
            pass

        copy_duplicity_backups.sync_files(
            src_dir, dst_dir,
            ["nonempty_file", "empty_file"], False, 0)
        dst_files = os.listdir(dst_dir)
        self.assertEqual(len(dst_files), 2)
        self.assertIn("nonempty_file", dst_files)
        self.assertIn("empty_file", dst_files)
        self.assertEqual(
            os.path.getsize(os.path.join(src_dir, "nonempty_file")),
            os.path.getsize(os.path.join(dst_dir, "nonempty_file")))
        self.assertEqual(
            os.path.getsize(os.path.join(src_dir, "empty_file")),
            os.path.getsize(os.path.join(dst_dir, "empty_file")))

        shutil.rmtree(folder)


    def test_07(self):
        '''Random files, some files available at destination'''
        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        rnd = random.Random()
        rnd.seed(28373332)
        src_files = gen_random_files(rnd, src_dir, 50)
        files_to_sync = src_files[-30:]
        for file_ in files_to_sync[:10]:
            shutil.copyfile(
                os.path.join(src_dir, file_),
                os.path.join(dst_dir, file_))

        copy_duplicity_backups.sync_files(src_dir, dst_dir, files_to_sync, False, 0)

        self.assertTrue(cmp_src_dst_files(src_dir, dst_dir, files_to_sync))
        shutil.rmtree(folder)


    def test_08(self):
        '''Random files, simulate partly transferred files'''

        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        rnd = random.Random()
        rnd.seed(332093199)
        src_files = gen_random_files(rnd, src_dir, 50)
        files_to_sync = src_files[-30:]
        for file_ in files_to_sync:
            shutil.copyfile(
                os.path.join(src_dir, file_),
                os.path.join(dst_dir, file_))

        files_to_truncate = []
        files_to_truncate.append(os.path.join(dst_dir, files_to_sync[-1]))
        files_to_truncate.append(os.path.join(dst_dir, files_to_sync[-2]))
        files_to_truncate.append(os.path.join(dst_dir, files_to_sync[-3]))

        for entry in files_to_truncate:
            with open(entry, mode="r+") as file_:
                new_size = os.path.getsize(entry)
                file_.truncate(new_size)

        copy_duplicity_backups.sync_files(src_dir, dst_dir, files_to_sync, False, 0)

        self.assertTrue(cmp_src_dst_files(src_dir, dst_dir, files_to_sync))
        shutil.rmtree(folder)


    def test_09(self):
        '''File size limit'''

        folder = self.gen_tempfolder()

        src_dir = os.path.join(folder, "src")
        dst_dir = os.path.join(folder, "dst")
        os.makedirs(src_dir)
        os.makedirs(dst_dir)

        gen_dummy_file(os.path.join(src_dir, "file1"), 20)
        gen_dummy_file(os.path.join(src_dir, "file2"), 30)
        gen_dummy_file(os.path.join(src_dir, "file3"), 20)

        max_size = 60

        copy_duplicity_backups.sync_files(
            src_dir, dst_dir,
            ["file1", "file2", "file3"],
            False, max_size)
        dst_files = os.listdir(dst_dir)

        self.assertEqual(len(dst_files), 2)
        dst_size = 0
        for file_ in dst_files:
            dst_size = dst_size + os.path.getsize(os.path.join(dst_dir, file_))
        self.assertTrue(dst_size <= max_size)

        shutil.rmtree(folder)

if __name__ == "__main__":
    unittest.main()
