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
    "S", # Flag "S" (seen): the user has viewed this message, though perhaps he didn't read all the way through it.
    "T", # Flag "T" (trashed): the user has moved this message to the trash; the trash will be emptied by a later user action.
    "D", # Flag "D" (draft): the user considers this message a draft; toggled at user discretion.
    "F"  # Flag "F" (flagged): user-defined flag; toggled at user discretion.
    ]



def parseMaildirFlags(fileName):
    '''Parses maildir flags encoded in fileName and returns a dict containing
    SUPPORTED_MAILDIR_FLAGS as key and true/false as value'''
    flags = {}
    for entry in SUPPORTED_MAILDIR_FLAGS:
        flags[entry] = False
    posInfo = fileName.find(":2,")
    if posInfo == -1:
        return flags
    i = posInfo + 3
    while i < len(fileName):
        for entry in SUPPORTED_MAILDIR_FLAGS:
            if entry == fileName[i]:
                flags[entry] = True
        i = i + 1
    return flags


def isMaildir(path):
    '''Checks if given path is a valid maildir'''
    return os.path.isdir(os.path.join(path, "cur")) and os.path.isdir(os.path.join(path, "new"))


def samePath(path1, path2):
    '''Returns true if two given pathes path1 and path2 point to the same location'''
    return os.path.abspath(path1) == os.path.abspath(path2)


def getFlaggedFiles(dir_):
    '''Returns a list of files in a maildir cur or new directory which have the
       F flag set'''
    flaggedFiles = []
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.isfile(path):
            flags = parseMaildirFlags(path)
            if flags["F"]:
                flaggedFiles.append(path)
    return flaggedFiles


def deleteSymlinks(dir_):
    '''Delete all symlinks in a directory. Returns false on any error, otherwise true'''
    success = True
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.islink(path):
            try:
                os.remove(path)
            except:
                print "Could not delete " + path
                success = False
    return success


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

    if not isMaildir(opt_maildir):
        print "Maildir cannot be opened"
        sys.exit(1)

    if not isMaildir(opt_vfolder):
        print "VFolder is not a maildir"
        sys.exit(1)

    flaggedFiles = []
    for dirpath, _, _ in os.walk(opt_maildir):
        if isMaildir(dirpath) and not samePath(dirpath, opt_vfolder):
            list_ = getFlaggedFiles(os.path.join(dirpath, "cur"))
            flaggedFiles.extend(list_)
            list_ = getFlaggedFiles(os.path.join(dirpath, "new"))
            flaggedFiles.extend(list_)


    success = deleteSymlinks(os.path.join(opt_vfolder, "cur"))
    success |= deleteSymlinks(os.path.join(opt_vfolder, "new"))
    i = 1 # Guarantee uniqueness of filenames
    for file_ in flaggedFiles:
        linkName = os.path.join(opt_vfolder, "cur", ("%05d" % i) + "_" + os.path.basename(file_))
        i += 1
        try:
            os.symlink(file_, linkName)
        except:
            print "Symlink cannot be created: " + linkName + " -> " + file_
            success = False

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "main":
    main()
