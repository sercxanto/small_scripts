#!/usr/bin/python
"""Searches flagged mails and symlinks them to a (vfolder) maildir"""
#
#    mutt_flagged_vfolder_link.py
#
#    Searches flagged mails and symlinks them to a (vfolder) maildir
#
#    Copyright (C) 2009-2018 Georg Lutz <georg AT NOSPAM georglutz DOT de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import sys


# See e.g. http://cr.yp.to/proto/maildir.html
SUPPORTED_MAILDIR_FLAGS = [
    "P", # Flag "P" (passed): the user has resent/forwarded/bounced this message to someone else.
    "R", # Flag "R" (replied): the user has replied to this message.
    "S", # Flag "S" (seen): the user has viewed this message,
         # though perhaps he didn't read all the way through it.
    "T", # Flag "T" (trashed): the user has moved this message to the trash;
         # the trash will be emptied by a later user action.
    "D", # Flag "D" (draft): the user considers this message a draft; toggled at user discretion.
    "F"  # Flag "F" (flagged): user-defined flag; toggled at user discretion.
    ]



def parse_maildir_flags(file_name):
    '''Parses maildir flags encoded in fileName and returns a dict containing
    SUPPORTED_MAILDIR_FLAGS as key and true/false as value'''
    flags = {}
    for entry in SUPPORTED_MAILDIR_FLAGS:
        flags[entry] = False
    pos_info = file_name.find(":2,")
    if pos_info == -1:
        return flags
    i = pos_info + 3
    while i < len(file_name):
        for entry in SUPPORTED_MAILDIR_FLAGS:
            if entry == file_name[i]:
                flags[entry] = True
        i = i + 1
    return flags


def is_maildir(path):
    '''Checks if given path is a valid maildir'''
    return os.path.isdir(os.path.join(path, "cur")) and os.path.isdir(os.path.join(path, "new"))


def is_same_path(path1, path2):
    '''Returns true if two given pathes path1 and path2 point to the same location'''
    return os.path.abspath(path1) == os.path.abspath(path2)


def get_flagged_files(dir_):
    '''Returns a list of files in a maildir cur or new directory which have the
       F flag set'''
    flagged_files = []
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.isfile(path):
            flags = parse_maildir_flags(path)
            if flags["F"]:
                flagged_files.append(path)
    return flagged_files


def delete_symlinks(dir_):
    '''Delete all symlinks in a directory. Returns false on any error, otherwise true'''
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.islink(path):
            os.remove(path)


def main():
    '''main function, called when script file is executed directly'''

    parser = argparse.ArgumentParser()
    parser.add_argument('maildir',
                        help='The Maildir with the original messages')
    parser.add_argument('vfolder',
                        help='The virtual maildir folder')

    args = parser.parse_args()

    opt_vfolder = os.path.expanduser(args.vfolder)
    opt_maildir = os.path.expanduser(args.maildir)

    if not is_maildir(opt_maildir):
        print "Maildir cannot be opened"
        sys.exit(1)

    if not is_maildir(opt_vfolder):
        print "VFolder is not a maildir"
        sys.exit(1)

    flagged_files = []
    for dirpath, _, _ in os.walk(opt_maildir):
        if is_maildir(dirpath) and not is_same_path(dirpath, opt_vfolder):
            list_ = get_flagged_files(os.path.join(dirpath, "cur"))
            flagged_files.extend(list_)
            list_ = get_flagged_files(os.path.join(dirpath, "new"))
            flagged_files.extend(list_)


    delete_symlinks(os.path.join(opt_vfolder, "cur"))
    delete_symlinks(os.path.join(opt_vfolder, "new"))
    i = 1 # Guarantee uniqueness of filenames
    for file_ in flagged_files:
        link_name = os.path.join(opt_vfolder, "cur", ("%05d" % i) + "_" + os.path.basename(file_))
        i += 1
        os.symlink(file_, link_name)

if __name__ == "main":
    main()
