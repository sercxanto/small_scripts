#!/usr/bin/python
# vim: set fileencoding=utf8 :
"""Yet another import script for gnucash"""

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


# standard library imports
import argparse
import csv
import datetime

# gnucash imports
import gnucash


# gnucash uses runtime generated members which are not handled by pylint:
# pylint: disable=no-member

def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Yet another import script for gnucash")
    parser.add_argument("csvfile", help="CSV file to import")
    parser.add_argument(
        "gnucashfile",
        help="gnucashfile to import the entries to")
    parser.add_argument(
        "accountname",
        help="account name for which the CSV entries should be imported")
    return parser.parse_args()


def get_account_from_path(parent_account, account_path):
    '''Recursively travels the path and returns a gnucash account

    parent_account: The parent account. For the first call the root account has to be passed.
    account_path: The path as an array relative to the parent.

    Returns None in case of error / if account is not found
    '''

    current_account_name = account_path[0]
    path_rest = account_path[1:]

    current_account = parent_account.lookup_by_name(current_account_name)
    if current_account is None:
        # Error case: the path could not be found
        return None
    if len(path_rest) > 0:
        return get_account_from_path(current_account, path_rest)
    else:
        return current_account


def check_account_names(root_account, account_names):
    '''Check the given list of accounts for availability in gnucash

    If all accounts exist returns an empty list
    Otherwise returns a list of account names which cannot be found.
    '''
    result = []
    for account_name in account_names:
        if get_account_from_path(root_account, account_name.split(":")) is None:
            result.append(account_name)

    return result


def get_session_from_file(filename):
    '''Returns a gnucash.Session for a given filename'''
    file_path = "file://" + filename
    return gnucash.Session(file_path)


class ParserErrorException(Exception):
    '''Exception error, parsing mismatch'''
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def get_parsed_csv_file(filename):
    '''Returns the parsed CSV file

    Expected CSV format:

        date; accountname; description; value

    * the first line must consist of the exact field names mentioned above
    * import starts at the second line
    * "date" is in the ISO8601 format
    * The decimal seperator for "value" is the dot.

    {
        date: 2017-01-01,
        accountname: "abc:def",
        description: "Some description text",
        value: 1.23
    }

    "date" is a python datetime object

    In case of any error during parsing an expection ParserErrorException is thrown.
    '''
    result = []
    expected_header = ["date", "accountname", "description", "value"]

    with open(filename, "rb") as filehandle:
        filereader = csv.reader(filehandle, delimiter=";")
        row_nr = 0
        for row in filereader:
            row_nr = row_nr + 1
            if row_nr == 1:
                if row != expected_header:
                    raise ParserErrorException("Header check mismatch")
            else:
                if len(row) != 4:
                    ParserErrorException("Length of line %d mismatch" % (row_nr))
                entry = {}
                entry["date"] = datetime.datetime.strptime(row[0], '%Y-%m-%d')
                entry["accountname"] = row[1]
                entry["description"] = row[2]
                entry["value"] = float(row[3])
                result.append(entry)
    return result


def create_gnc_numeric(value):
    '''Returns a gnucash.GncNumeric for the given value'''
    # Unfortunately there is no way in the python version to call something like
    # double_to_gnc_numeric so we stay with the standard denominator 100 Gnucash is using
    # in all places (see XML file).
    # There is one caveat: the float value has to be rounded, otherwise python just cuts it off.
    # test e.g. with 17.49
    return gnucash.GncNumeric(int(round(value*100)), 100)


def create_simple_transaction(book, date_posted, src_account, dst_account, value, description):
    '''Creates a gnucash transaction with two splits for the given data

       book: the gnucash book to create the transaction in
       date_posted: The posted date for the transaction
       src_account: source account, type gnucash.Account, value will be negative
       dst_account: destination account, type gnucash.Account
       value: Value as float, currency will be taken from the src_account
       description: Description field for the transaction

       Does not have a return value.
    '''
    transaction = gnucash.Transaction(book)
    transaction.BeginEdit()
    currency = src_account.GetCommodity()
    transaction.SetCurrency(currency)
    transaction.SetDescription(description)
    transaction.SetDateEnteredTS(datetime.datetime.now())
    transaction.SetDatePostedTS(date_posted)

    amount = create_gnc_numeric(value)

    split1 = gnucash.Split(book)
    split1.SetParent(transaction)
    split1.SetAccount(dst_account)
    split1.SetValue(amount.neg())
    split1.SetAmount(amount.neg())

    split2 = gnucash.Split(book)
    split2.SetParent(transaction)
    split2.SetAccount(src_account)
    split2.SetValue(amount)
    split2.SetAmount(amount)

    transaction.CommitEdit()


def import_csv_file(csv_filename, gnucash_filename, src_account_name):
    '''Imports a CSV file to a gnucash file for the given account

    csv_filename: The file with the CSV data
    gnucash_filename: Gnucash file to import data to
    src_account_name: Gnucash account name for which the CSV entries should be imported

    Returns a dict with the result:

    {
        nr_imported: 0, # nr of imported items, <0 in case of error
        msg: "my message" # describing (error) message
    }

    '''

    result = {
        "nr_imported": 0,
        "msg": ""
    }
    parsed_csv = get_parsed_csv_file(csv_filename)

    if len(parsed_csv) == 0:
        result["msg"] = "No entries in CSV file"
        return result

    session = get_session_from_file(gnucash_filename)
    book = session.book
    root_account = book.get_root_account()

    src_account = get_account_from_path(root_account, src_account_name.split(":"))

    if src_account is None:
        result["nr_imported"] = -1
        result["msg"] = "Missing src account in gnucash"
        session.end()
        session.destroy()
        return result

    account_names = []
    for entry in parsed_csv:
        account_names.append(entry["accountname"])
    missing_accounts = check_account_names(root_account, account_names)
    if len(missing_accounts) > 0:
        result["nr_imported"] = -1
        result["msg"] = "The following accounts could not be found in gnucash:"
        for entry in missing_accounts:
            result["msg"] += " " + entry
        session.end()
        session.destroy()
        return result

    for entry in parsed_csv:
        dst_account = get_account_from_path(root_account, entry["accountname"].split(":"))

        create_simple_transaction(
            book, entry["date"], src_account, dst_account, entry["value"], entry["description"])
        result["nr_imported"] += 1

    session.save()
    session.end()
    session.destroy()

    return result


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    result = import_csv_file(args.csvfile, args.gnucashfile, args.accountname)

    if result["nr_imported"] < 0:
        print "An error occured: " + result["msg"]
    else:
        print "Imported %d entries" % (result["nr_imported"])

if __name__ == "__main__":
    main()
