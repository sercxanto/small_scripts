#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""tests for find_orphaned_sidecar_files.py"""

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
import os
import sys
import unittest
import unittest.mock


TESTSCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import find_orphaned_sidecar_files # pylint: disable=import-error,wrong-import-position


class TestOrphanedFiles(unittest.TestCase):
    '''test get_orphaned_files'''

    def test_empty_file_list_files(self):
        '''Empty list of input files'''

        sidecar_extensions = ["abc"]
        list_of_files = []
        expected_result = []
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


    def test_no_extensions(self):
        '''Only files with no extensions'''

        sidecar_extensions = ["abc"]
        list_of_files = [
            "somefile",
            "some_other_file"
        ]
        expected_result = []
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


    def test_only_dotfiles(self):
        '''Files with leading dots'''

        sidecar_extensions = ["abc"]
        list_of_files = [
            ".dotfile1",
            ".dotfile2"
        ]
        expected_result = []
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


    def test_no_orphans(self):
        '''No orphans'''

        sidecar_extensions = ["xmp", "otherext"]
        list_of_files = [
            "file1.jpg",
            "file1.jpg.xmp",
            "file2.jpg",
            "file2.jpg.XMP",
            "file3.xmp",
            "file3.jpg"
        ]
        expected_result = []
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


    def test_orphans(self):
        '''orphans'''

        sidecar_extensions = ["xmp"]
        list_of_files = [
            "file1.jpg",
            "file1.jpg.xmp",
            "file2.jpg.XMP"
        ]
        expected_result = [
            "file2.jpg.XMP"
        ]
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


    def test_no_orphans_multiple_exts(self):
        '''test multiple extensions'''

        sidecar_extensions = ["xmp"]
        list_of_files = [
            "file1",
            "file1.abc.xmp",
        ]
        expected_result = [
            "file1.abc.xmp"
        ]
        result = find_orphaned_sidecar_files.get_orphaned_files(list_of_files, sidecar_extensions)
        self.assertEqual(result, expected_result)


class TestFindFiles(unittest.TestCase):
    '''test find_files'''

    def test_find_files_simple(self):
        '''test simple use case'''

        sidecar_extensions = ["xmp"]
        # mocks (root, dirs, files)
        # dir2 is empty
        filetree = [
            ('/', ('dir1', 'dir2'), ('file1.xmp')),
            ('/dir1', (), ('file1.jpg', 'file1.xmp', 'file2.xmp')),
            ('/dir2', (), ())
        ]
        expected = [
            "/dir1/file2.xmp"
        ]

        with unittest.mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = filetree
            result = list(find_orphaned_sidecar_files.find_files("/", sidecar_extensions))
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
