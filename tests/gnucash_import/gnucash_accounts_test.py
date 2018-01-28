#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" tests for gnucash_accounts.py"""

# gnucash_accounts.py - Get list of accounts from gnucash
# Copyright (C) 2018 Georg Lutz
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
import os
import sys
import unittest

# own imports
TESTSCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
SCRIPT_DIR = os.path.realpath(os.path.join(TESTSCRIPT_DIR, os.pardir, os.pardir))
sys.path.append(SCRIPT_DIR)
import gnucash_accounts # pylint: disable=import-error,wrong-import-position


class TestAccounts(unittest.TestCase):
    '''test account list'''

    def test_accountlist(self):
        '''Check account list'''

        myfile = os.path.join(TESTSCRIPT_DIR, "mytest.gnucash")

        calculated = gnucash_accounts.get_flat_account_list(myfile)

        with open(os.path.join(TESTSCRIPT_DIR, "account_list.txt"), "r") as filehandle:
            expected = filehandle.readlines()
        expected = [element.strip("\n") for element in expected]

        self.assertEqual(calculated, expected)

if __name__ == "__main__":
    unittest.main(verbosity=20)
