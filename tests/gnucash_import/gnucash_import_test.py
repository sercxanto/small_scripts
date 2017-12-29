#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" tests for gnucash_import.py"""

# gnucash_import.py - Yet another import script for gnucash
# Copyright (C) 2017 Georg Lutz
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Standard library imports:
import datetime
import os
import shutil
import sys
import tempfile
import unittest

# gnucash imports
import gnucash

# own imports
TESTSCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import gnucash_import # pylint: disable=import-error,wrong-import-position

# pylint: disable=no-member


class TestAccounts(unittest.TestCase):
    '''test account list'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_georgstest")

    def test_01(self):
        '''Existing account'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        my_account_name = "Aktiva:Barvermögen:Girokonto"
        my_account = gnucash_import.get_account_from_path(root_account, my_account_name.split(":"))

        self.assertIsNotNone(my_account)
        self.assertEqual(my_account.GetName(), "Girokonto")

        session.end()
        session.destroy()

    def test_02(self):
        '''Existing top level account'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        my_account_name = "Aktiva"
        my_account = gnucash_import.get_account_from_path(root_account, my_account_name.split(":"))

        self.assertIsNotNone(my_account)
        self.assertEqual(my_account.GetName(), "Aktiva")

        session.end()
        session.destroy()

    def test_03(self):
        '''Non existing account'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        my_account_name = "Aktiva:Barvermögen:Girokontoxx"
        my_account = gnucash_import.get_account_from_path(root_account, my_account_name.split(":"))

        self.assertIsNone(my_account)

        session.end()
        session.destroy()

    def test_04(self):
        '''Non existing top level account'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        my_account_name = "Aktivaxxx:Barvermögen:Girokonto"
        my_account = gnucash_import.get_account_from_path(root_account, my_account_name.split(":"))

        self.assertIsNone(my_account)

        session.end()
        session.destroy()

    def test_05(self):
        '''check account names - existing accounts'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        account_names = ["Aktiva:Barvermögen:Girokonto", "Aktiva:Barvermögen:Bargeld"]
        missing_accounts = gnucash_import.check_account_names(root_account, account_names)
        self.assertEqual(len(missing_accounts), 0)

        session.end()
        session.destroy()

    def test_06(self):
        '''check account names - nonexisting accounts'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")
        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        account_names = ["Aktiva:Barvermögen:Girokonto", "Aktiva:Barvermögen:Bargeldxxx"]
        expected = ["Aktiva:Barvermögen:Bargeldxxx"]
        calculated = gnucash_import.check_account_names(root_account, account_names)
        self.assertItemsEqual(calculated, expected)

        session.end()
        session.destroy()


class TestTransactions(unittest.TestCase):
    '''test transactions'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_georgstest")

    def test_01(self):
        '''Add transaction and check balance of accounts'''

        tempfolder = self.gen_tempfolder()
        shutil.copy(os.path.join(TESTSCRIPT_DIR, "mytest.gnucash"), tempfolder)
        myfile = os.path.join(tempfolder, "mytest.gnucash")

        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        src_account_name = "Aktiva:Barvermögen:Girokonto"
        src_account = gnucash_import.get_account_from_path(
            root_account, src_account_name.split(":"))

        dst_account_name = "Aktiva:Barvermögen:Bargeld"
        dst_account = gnucash_import.get_account_from_path(
            root_account, dst_account_name.split(":"))

        transaction = gnucash.Transaction(book)
        transaction.BeginEdit()
        transaction.SetNum("Some Nr.")
        transaction.SetNotes("Some Notes")
        transaction.SetDescription("Some Description")
        currency = src_account.GetCommodity()
        transaction.SetCurrency(currency)
        transaction.SetDateEnteredTS(datetime.datetime.now())
        transaction.SetDatePostedTS(datetime.datetime.now())

        amount = gnucash.GncNumeric(123, 100)

        split1 = gnucash.Split(book)
        split1.SetParent(transaction)
        split1.SetAccount(dst_account)
        split1.SetValue(amount)
        split1.SetAmount(amount)
        split1.SetMemo("Memo split1")

        split2 = gnucash.Split(book)
        split2.SetParent(transaction)
        split2.SetAccount(src_account)
        split2.SetValue(amount.neg())
        split2.SetAmount(amount.neg())
        split2.SetMemo("Memo split2")

        transaction.CommitEdit()

        session.save()
        session.end()
        session.destroy()

        session = gnucash_import.get_session_from_file(myfile)
        book = session.book
        root_account = book.get_root_account()

        src_account_name = "Aktiva:Barvermögen:Girokonto"
        src_account = gnucash_import.get_account_from_path(
            root_account, src_account_name.split(":"))

        dst_account_name = "Aktiva:Barvermögen:Bargeld"
        dst_account = gnucash_import.get_account_from_path(
            root_account, dst_account_name.split(":"))

        balance_src = src_account.GetBalance()
        balance_dst = dst_account.GetBalance()

        expected_value = gnucash.GncNumeric(123, 100)
        self.assertTrue(gnucash.GncNumeric.equal(balance_dst, expected_value))
        self.assertTrue(gnucash.GncNumeric.equal(balance_src, expected_value.neg()))

        session.end()
        session.destroy()

        shutil.rmtree(tempfolder)


class TestCsvParsing(unittest.TestCase):
    '''test parsing CSV files'''

    def test_01(self):
        '''parse_ok.csv'''
        filename = os.path.join(TESTSCRIPT_DIR, "parse_ok.csv")
        parsed = gnucash_import.get_parsed_csv_file(filename)

        expected = [
            {"date": datetime.datetime(2017, 1, 1),
             "accountname": "abcd:efg",
             "description": "Some description",
             "value": 2.31
            },
            {"date": datetime.datetime(2017, 1, 2),
             "accountname": "xyz:abc",
             "description": "Some other description",
             "value": 1.23
            }
        ]
        self.assertListEqual(parsed, expected)

    def test_02(self):
        '''parse_nok.csv'''
        filename = os.path.join(TESTSCRIPT_DIR, "parse_nok.csv")

        try:
            gnucash_import.get_parsed_csv_file(filename)
        except:
            pass
        else:
            self.fail("Exception not raised")


class TestCsvImport(unittest.TestCase):
    '''test importing CSV files'''

    @staticmethod
    def gen_tempfolder():
        '''Returns temporary folder name'''
        return tempfile.mkdtemp(prefix="tmp_georgstest")

    def test_01(self):
        '''Add transaction and check balance of accounts'''

        tempfolder = self.gen_tempfolder()
        shutil.copy(os.path.join(TESTSCRIPT_DIR, "mytest.gnucash"), tempfolder)
        gnucash_file = os.path.join(tempfolder, "mytest.gnucash")
        csv_file = os.path.join(TESTSCRIPT_DIR, "import_1.csv")
        calculated = gnucash_import.import_csv_file(
            csv_file,
            gnucash_file,
            "Aktiva:Barvermögen:Girokonto")
        self.assertEqual(calculated["nr_imported"], 2)

        session = gnucash_import.get_session_from_file(gnucash_file)
        book = session.book
        root_account = book.get_root_account()

        src_account_name = "Aktiva:Barvermögen:Girokonto"
        src_account = gnucash_import.get_account_from_path(
            root_account, src_account_name.split(":"))

        dst_account_name = "Aktiva:Barvermögen:Bargeld"
        dst_account = gnucash_import.get_account_from_path(
            root_account, dst_account_name.split(":"))

        balance_src = src_account.GetBalance()
        balance_dst = dst_account.GetBalance()

        expected_value = gnucash.GncNumeric(354, 100)
        self.assertTrue(gnucash.GncNumeric.equal(balance_dst, expected_value.neg()))
        self.assertTrue(gnucash.GncNumeric.equal(balance_src, expected_value))

        dst_splits = dst_account.GetSplitList()
        src_splits = src_account.GetSplitList()

        self.assertEqual(len(dst_splits), 2)
        self.assertEqual(len(src_splits), 2)

        shutil.rmtree(tempfolder)




if __name__ == "__main__":
    unittest.main(verbosity=20)
