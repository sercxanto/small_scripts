#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" tests for fix_comdirect_csv.py"""

# The MIT License (MIT)
#
# Copyright (c) 2019 Georg Lutz
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
import fix_comdirect_csv # pylint: disable=import-error,wrong-import-position


class TestSplitBuchungstext(unittest.TestCase):
    '''split_buchungstext function'''

    def test_01(self):
        '''Simple example'''

        list_of_fields = ["first", "second", "third"]
        buchungstext = "first:abcfirstsecond:abcsecond third:abcthird"

        expected_result = {
            "first": "abcfirst",
            "second": "abcsecond",
            "third": "abcthird"
        }

        result = fix_comdirect_csv.split_buchungstext(list_of_fields, buchungstext)
        self.assertDictEqual(result, expected_result)

    def test_02(self):
        '''Reverse order'''

        list_of_fields = ["first", "second", "third"]
        buchungstext = "third:abcthirdsecond:abcsecond first:abcfirst"

        expected_result = {
            "first": "abcfirst",
            "second": "abcsecond",
            "third": "abcthird"
        }

        result = fix_comdirect_csv.split_buchungstext(list_of_fields, buchungstext)
        self.assertDictEqual(result, expected_result)

    def test_03(self):
        '''Reverse order list_of_fields'''

        list_of_fields = ["third", "first", "second"]
        buchungstext = "first:abcfirstsecond:abcsecond third:abcthird"

        expected_result = {
            "first": "abcfirst",
            "second": "abcsecond",
            "third": "abcthird"
        }

        result = fix_comdirect_csv.split_buchungstext(list_of_fields, buchungstext)
        self.assertDictEqual(result, expected_result)

    def test_04(self):
        '''Non existing list of field entry'''

        list_of_fields = ["first", "second", "third", "non_existing"]
        buchungstext = "first:abcfirstsecond:abcsecond third:abcthird"

        expected_result = {
            "first": "abcfirst",
            "second": "abcsecond",
            "third": "abcthird"
        }

        result = fix_comdirect_csv.split_buchungstext(list_of_fields, buchungstext)
        self.assertDictEqual(result, expected_result)


class TestGiroReader(unittest.TestCase):
    '''GiroReader class'''

    def test_01(self):
        '''Standard test'''

        in_record = {
            "buchungstag": "05.08.2019",
            "valuta": "05.08.2019",
            "vorgang": "Übertrag/Überweisung",
            "buchungstext": "Auftraggeber:auftragnameBuchungstext: Der Buchungstext 123 456Empfänger: nameKto/IBAN: DE123 BLZ/BIC: ABC123",
            "umsatz": "-139,40"
        }

        out_record_expected = {
            "date": datetime.date(2019, 8, 5),
            "valuta": datetime.date(2019, 8, 5),
            "initiator": "auftragname",
            "payee":
                {
                    "name": "name",
                    "account_id": "DE123",
                    "bic": "ABC123"
                },
            "info": "Der Buchungstext 123",
            "memo": "Auftraggeber:auftragnameBuchungstext: Der Buchungstext 123 456Empfänger: nameKto/IBAN: DE123 BLZ/BIC: ABC123",
            "amount": -139.40,
        }

        giro_reader = fix_comdirect_csv.GiroReader()
        out_record = giro_reader.convert_record(in_record)
        self.assertEqual(out_record["date"], out_record_expected["date"])
        self.assertEqual(out_record["valuta"], out_record_expected["valuta"])
        self.assertEqual(out_record["amount"], out_record_expected["amount"])
        self.assertEqual(out_record["memo"], out_record_expected["memo"])
        self.assertDictEqual(out_record["payee"], out_record_expected["payee"])
        self.assertDictEqual(out_record, out_record_expected)


    def test_02(self):
        '''Kartenverfügung, payee in buchungstext'''

        in_record = {
            "buchungstag" : "02.09.2019",
            "valuta" : "02.09.2019",
            "vorgang": "Kartenverfügung",
            "buchungstext": " Buchungstext: IKEA DT. NL ORTORTORTORT//ORTORTORT 2019-08-30T14:58:04 KFN 1 Ref. 3XY7515557812479/39702 ",
            "umsatz": "-48,91"
        }
        out_record_expected = {
            "date": datetime.date(2019, 9, 2),
            "valuta": datetime.date(2019, 9, 2),
            "initiator": None,
            "payee":
                {
                    "name": "IKEA DT. NL ORTORTORTORT//ORTORTORT",
                    "account_id": None,
                    "bic": None
                },
            "info": "IKEA DT. NL",
            "memo": " Buchungstext: IKEA DT. NL ORTORTORTORT//ORTORTORT 2019-08-30T14:58:04 KFN 1 Ref. 3XY7515557812479/39702 ",
            "amount": -48.91,
        }
        giro_reader = fix_comdirect_csv.GiroReader()
        out_record = giro_reader.convert_record(in_record)
        self.assertDictEqual(out_record, out_record_expected)

if __name__ == "__main__":
    unittest.main()
