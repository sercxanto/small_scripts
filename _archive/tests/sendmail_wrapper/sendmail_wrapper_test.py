#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" sendmail_wrapper_test.py"""

# The MIT License (MIT)
#
# Copyright (c) 2020 Georg Lutz
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

import inspect
import json
import os
import sys
import unittest

TESTSCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import sendmail_wrapper # pylint: disable=import-error,wrong-import-position


class TestPatchMessage(unittest.TestCase):
    '''Test patch_message'''

    @staticmethod
    def read_whole_file(filename):
        '''Read whole file, return string'''
        # newline='': The mail*_expected files ar encoded with CRLF line ending already
        with open(filename, mode='r', newline='') as file_:
            result = file_.read()
        return result

    @staticmethod
    def call_patchmessage_with_files(testname):
        '''Calls patchmessage with the filenames deduced from testname

        Returns a tuple

        ("patched string", "expected string")

        Where "patched string" is the output of patchmessage and "expected string" is the content
        of the "*_expected.txt files
        '''
        in_filename = os.path.join(TESTSCRIPT_DIR, "{}_in.txt".format(testname))
        expected_filename = os.path.join(TESTSCRIPT_DIR, "{}_expected.txt".format(testname))
        settings_filename = os.path.join(TESTSCRIPT_DIR, "{}_settings.json".format(testname))

        with open(settings_filename) as file_:
            settings = json.load(file_)

        with open(in_filename, "r") as file_:
            calculated = sendmail_wrapper.patch_message(
                file_, settings["from_address"], settings["to_address"], None)
        expected = TestPatchMessage.read_whole_file(os.path.join(TESTSCRIPT_DIR, expected_filename))

        return (calculated, expected)

    def test_01_unchanged(self):
        '''Input=Output, no changes necessary'''
        testname = inspect.getframeinfo(inspect.currentframe()).function
        calculated, expected = self.call_patchmessage_with_files(testname)
        self.assertEqual(calculated, expected)

    def test_02_changed_from_to(self):
        '''Change from and to header'''
        testname = inspect.getframeinfo(inspect.currentframe()).function
        calculated, expected = self.call_patchmessage_with_files(testname)
        self.assertEqual(calculated, expected)

    def test_03_utf8(self):
        '''UTF8 content'''
        testname = inspect.getframeinfo(inspect.currentframe()).function
        calculated, expected = self.call_patchmessage_with_files(testname)
        self.assertEqual(calculated, expected)

    def test_04_missing_fromto(self):
        '''UTF8 content'''
        testname = inspect.getframeinfo(inspect.currentframe()).function
        calculated, expected = self.call_patchmessage_with_files(testname)
        self.assertEqual(calculated, expected)

if __name__ == "__main__":
    unittest.main()
