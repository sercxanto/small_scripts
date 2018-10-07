#!/usr/bin/python
#
#    mutt_flagged_vfolder_link.py
#
#    Searches flagged mails and symlinks them to a (vfolder) maildir
#
#    Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>
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

import optparse
import os
import sys

VERSIONSTRING = "0.1"

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
    if os.path.isdir(os.path.join(path, "cur")) and os.path.isdir(os.path.join(path, "new")):
        return True
    else:
        return False


def samePath(path1, path2):
    '''Returns true if two given pathes path1 and path2 point to the same location'''
    if os.path.abspath(path1) == os.path.abspath(path2):
        return True
    else:
        return False


def getFlaggedFiles(dir):
    '''Returns a list of files in a maildir cur or new directory which have the
       F flag set'''
    flaggedFiles = []
    entries = os.listdir(dir)
    for entry in entries:
        path = os.path.join(dir, entry)
        if os.path.isfile(path):
            flags = parseMaildirFlags(path)
            if flags["F"]:
                flaggedFiles.append(path)
    return flaggedFiles


def deleteSymlinks(dir):
    '''Delete all symlinks in a directory. Returns false on any error, otherwise true'''
    success = True
    entries = os.listdir(dir)
    for entry in entries:
        path = os.path.join(dir, entry)
        if os.path.islink(path):
            try:
                os.remove(path)
            except:
                print "Could not delete " + path
                success = False
    return success



########### MAIN PROGRAM #############

parser = optparse.OptionParser(
    usage="%prog [options] Maildir vfolderpath",
    version="%prog " + VERSIONSTRING + os.linesep +
    "Copyright (C) 2010 Georg Lutz <georg AT NOSPAM georglutz DOT de")

(options, args) = parser.parse_args()

if len(args) < 2:
    parser.print_help()
    sys.exit(2)

optMaildir = os.path.expanduser(args[0])
optVFolder = os.path.expanduser(args[1])


if not isMaildir(optMaildir):
    print "Maildir cannot be opened"
    sys.exit(1)

if not isMaildir(optVFolder):
    print "VFolder is not a maildir"
    sys.exit(1)

flaggedFiles = []
for dirpath, dirnames, filenames in os.walk(optMaildir):
    if isMaildir(dirpath) and not samePath(dirpath, optVFolder):
        list = getFlaggedFiles(os.path.join(dirpath, "cur"))
        flaggedFiles.extend(list)
        list = getFlaggedFiles(os.path.join(dirpath, "new"))
        flaggedFiles.extend(list)


success = deleteSymlinks(os.path.join(optVFolder, "cur"))
success |= deleteSymlinks(os.path.join(optVFolder, "new"))
i = 1 # Guarantee uniqueness of filenames
for file in flaggedFiles:
    linkName = os.path.join(optVFolder, "cur", ("%05d" % i) + "_" + os.path.basename(file))
    i += 1
    try:
        os.symlink(file, linkName)
    except:
        print "Symlink cannot be created: " + linkName + " -> " + file
        success = False

if success:
    sys.exit(0)
else:
    sys.exit(1)
