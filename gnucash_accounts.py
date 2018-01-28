#!/usr/bin/python
# vim: set fileencoding=utf8 :
"""Get list of accounts from gnucash"""

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


# standard library imports
import argparse

# gnucash imports
import gnucash


# gnucash uses runtime generated members which are not handled by pylint:
# pylint: disable=no-member

def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Get list of accounts from gnucash")
    parser.add_argument(
        "gnucashfile",
        help="gnucashfile to get the account list from")
    return parser.parse_args()


def get_session_from_file(filename):
    '''Returns a gnucash.Session for a given filename'''
    file_path = "file://" + filename
    return gnucash.Session(file_path)


def get_children(account, level=0):
    '''Traveres account hierarchy and returns pathes

    account: The starting account
    level: Internal variable, don't use

    Example:

        * account1
            * account2
            * account3
        * account4

    will return the list

        * account1:account2
        * account1:account3
        * account4
    '''
    result = []
    has_childs = False
    for child in account.get_children():
        has_childs = True
        subresult = get_children(child, level + 1)
        if level > 0:
            subresult = [account.GetName() + ":" + element for element in subresult]
        result = result + subresult
    if not has_childs and not account.GetPlaceholder():
        # Leaf level, ommit placeholders
        result.append(account.GetName())
    return result


def get_flat_account_list(filename):
    '''
    Returns flat account list from a gnucash file
    '''

    session = get_session_from_file(filename)
    book = session.book
    root_account = book.get_root_account()
    result = get_children(root_account)
    result.sort()
    session.end()
    session.destroy()
    return result


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    result = get_flat_account_list(args.gnucashfile)

    for entry in result:
        print entry

if __name__ == "__main__":
    main()
