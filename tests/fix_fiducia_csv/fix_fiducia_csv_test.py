#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" tests for fix_fiducia_csv.py"""

# The MIT License (MIT)
#
# Copyright (c) 2016-2018 Georg Lutz
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
import datetime
import filecmp
import os
import shutil
import sys
import tempfile
import unittest

TESTSCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import fix_fiducia_csv # pylint: disable=import-error,wrong-import-position


class TestFixFile(unittest.TestCase):
    '''overall test / fix_file function'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_fix_fiducia_csv_tests")

    def test_01(self):
        '''Standard test'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data.csv")
        out_filepath = os.path.join(temp_folder, "out.csv")
        with open(out_filepath, mode="wb") as out_file:
            fix_fiducia_csv.fix_file(in_filepath, None, None, out_file)

        expected_out_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data_fixed.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)

    def test_02(self):
        '''Standard test with mapping'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data.csv")
        in_mapping_file_path = os.path.join(TESTSCRIPT_DIR, "mapping_sample_fiducia_data.csv")
        out_filepath = os.path.join(temp_folder, "out.csv")
        with open(out_filepath, mode="wb") as out_file:
            fix_fiducia_csv.fix_file(in_filepath, in_mapping_file_path, None, out_file)

        expected_out_filepath = os.path.join(
            TESTSCRIPT_DIR,
            "sample_fiducia_data_mapping_fixed.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)

    def test_03(self):
        '''Startdate all records'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data.csv")
        out_filepath = os.path.join(temp_folder, "out.csv")
        with open(out_filepath, mode="wb") as out_file:
            fix_fiducia_csv.fix_file(in_filepath, None, datetime.datetime(2016, 1, 1), out_file)

        expected_out_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data_fixed.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)

    def test_04(self):
        '''Startdate two records'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data.csv")
        out_filepath = os.path.join(temp_folder, "out.csv")
        with open(out_filepath, mode="wb") as out_file:
            fix_fiducia_csv.fix_file(in_filepath, None, datetime.datetime(2016, 6, 5), out_file)

        expected_out_filepath = os.path.join(
            TESTSCRIPT_DIR,
            "sample_fiducia_data_fixed_startdate_tworecords.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)

    def test_05(self):
        '''Startdate no records'''

        temp_folder = self.gen_tempfolder()
        in_filepath = os.path.join(TESTSCRIPT_DIR, "sample_fiducia_data.csv")
        out_filepath = os.path.join(temp_folder, "out.csv")
        with open(out_filepath, mode="wb") as out_file:
            fix_fiducia_csv.fix_file(in_filepath, None, datetime.datetime(2016, 6, 20), out_file)

        expected_out_filepath = os.path.join(
            TESTSCRIPT_DIR,
            "sample_fiducia_data_fixed_startdate_norecords.csv")
        self.assertTrue(filecmp.cmp(out_filepath, expected_out_filepath, shallow=False))
        shutil.rmtree(temp_folder)


class TestReadMapping(unittest.TestCase):
    '''Test read_mapping function'''

    def test_empty(self):
        '''read mapping_empty.csv'''
        in_mapping = os.path.join(TESTSCRIPT_DIR, "mapping_empty.csv")
        try:
            fix_fiducia_csv.read_mapping(in_mapping)
        except fix_fiducia_csv.ParserErrorException:
            pass
        else:
            self.fail("Exception not raised")

    def test_invalidheader(self):
        '''read mapping_invalidheader.csv'''
        in_mapping = os.path.join(TESTSCRIPT_DIR, "mapping_invalidheader.csv")
        try:
            fix_fiducia_csv.read_mapping(in_mapping)
        except fix_fiducia_csv.ParserErrorException:
            pass
        else:
            self.fail("Exception not raised")

    def test_invalidformat(self):
        '''read mapping_invalidformat.csv'''
        in_mapping = os.path.join(TESTSCRIPT_DIR, "mapping_invalidformat.csv")
        try:
            fix_fiducia_csv.read_mapping(in_mapping)
        except fix_fiducia_csv.ParserErrorException:
            pass
        else:
            self.fail("Exception not raised")

    def test_nomapping(self):
        '''read mapping_nomapping.csv'''
        in_mapping = os.path.join(TESTSCRIPT_DIR, "mapping_nomapping.csv")
        expected = {
            "account": [],
            "description": [],
            "searchterm1": [],
            "searchterm2": []
        }
        calculated = fix_fiducia_csv.read_mapping(in_mapping)
        self.assertEqual(calculated, expected)

    def test_mapping1(self):
        '''read mapping1.csv'''
        in_mapping = os.path.join(TESTSCRIPT_DIR, "mapping1.csv")
        expected = {
            "account":  ["account:myname1", "account:myname2", "account:myname3"],
            "description":  ["text1", "text2", "text3"],
            "searchterm1": ["searchterm11", "searchterm21", "searchterm31"],
            "searchterm2": ["searchterm22", "", ""]
        }
        calculated = fix_fiducia_csv.read_mapping(in_mapping)
        self.assertEqual(calculated, expected)


class TestGetMapped(unittest.TestCase):
    '''Test get_mapped function'''

    def test_noinput_nomapping(self):
        '''test empty mapping and empty input'''
        row = []
        mapping = {
            "account": [],
            "description": [],
            "searchterm1": [],
            "searchterm2": []
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertIsNone(calculated)

    def test_nomapping(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": [],
            "description": [],
            "searchterm1": [],
            "searchterm2": []
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertIsNone(calculated)

    def test_nomatch(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["nomatch", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertIsNone(calculated)

    def test_match_first_word(self):
        '''test match for first word'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["word1", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "sometext"])

    def test_match_substring(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["wor", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "sometext"])

    def test_match_second_word(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["word2", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "sometext"])

    def test_match_second_row(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["word3", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "sometext"])

    def test_match_last_row(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["word4", "stillnomatch"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "sometext"])

    def test_match_second_mapping(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["sometext", "someothertext"],
            "searchterm1": ["wordx", "word2"],
            "searchterm2": ["", ""]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["someother:account", "someothertext"])

    def test_match_second_searchterm(self):
        '''test empty mapping and non matching'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["thisshouldmatch", "this should not match"],
            "searchterm1": ["word1", "wordx"],
            "searchterm2": ["word2", "word2"]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "thisshouldmatch"])

    def test_match_second_searchterm2(self):
        '''first match only'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["thisshouldmatch", "this should not match"],
            "searchterm1": ["word4", "wordx"],
            "searchterm2": ["word2", "word2"]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "thisshouldmatch"])

    def test_match_two_matches(self):
        '''only first match should return string'''
        row = ["word1 word2", "word3", "word4"]
        mapping = {
            "account": ["some:account", "someother:account"],
            "description": ["thisshouldmatch", "this should not match"],
            "searchterm1": ["word1", "word1"],
            "searchterm2": ["word2", "word2"]
        }
        calculated = fix_fiducia_csv.get_mapped_text(row, mapping)
        self.assertEqual(calculated, ["some:account", "thisshouldmatch"])



if __name__ == "__main__":
    unittest.main()
