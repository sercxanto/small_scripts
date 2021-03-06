#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" paypal2homebank_test.py"""

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
import filecmp
import os
import shutil
import sys
import tempfile
import unittest

TESTSCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import paypal2homebank # pylint: disable=import-error,wrong-import-position


class Testpaypal2homebank(unittest.TestCase):
    '''overall test'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_paypal2homebank_tests")

    def test_01(self):
        '''Standard test'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "paypal.csv")
        out_filepath = os.path.join(temp_folder, "homebank.csv")
        with open(out_filepath, mode="w", encoding="utf-8") as out_file:
            paypal2homebank.paypal2homebank(in_filepath, out_file)

        expected_out_filepath = os.path.join(TESTSCRIPT_DIR, "homebank_expected.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)


if __name__ == "__main__":
    unittest.main()
