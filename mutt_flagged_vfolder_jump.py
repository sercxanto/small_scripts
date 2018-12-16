#!/usr/bin/python
"""Generates mutt command file to jump to the source of a symlinked mail"""
from __future__ import print_function
#
#    mutt_flagged_vfolder_jump.py
#
#    Generates mutt command file to jump to the source of a symlinked mail
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
import re
import sys


def parse_message_id(file_):
    '''Returns the message id for a given file.
    It is assumed that file represents a valid RFC822 message'''
    prog = re.compile("^Message-ID: (.+)", re.IGNORECASE)
    msg_id = ""
    for line in file_:
       # Stop after Header
        if len(line) < 2:
            break
        result = prog.search(line)
        if result is not None and len(result.groups()) == 1:
            msg_id = result.groups()[0]
            break
    return msg_id.strip("<>")


def parse_maildir(filename):
    '''Returns the maildir folder for a given file in a maildir'''
    (head, _) = os.path.split(os.path.dirname(filename))
    return head


def write_cmd_file(filename, maildir, msg_id):
    '''Writes a file which can be directly sourced by mutt. The file causes
       mutt to change to the given maildir and search there for the given
       message id.'''
    file_ = open(filename, "w")

    cmd = "push \"<change-folder> " + maildir + "<enter>/~i "
    # Helps if matching something like 123@[1.2.3.4]
    regex = re.escape(msg_id)
    # Replace dollar sign "$" with ".+" as mutt has problems with push
    # commands and a dollar sign followed with a non numeric value e.g. like "$u".
    # This seems to reference a variable and cannot be escaped apparently.
    # Something like "$1" does not oppose problems when escaped.
    regex = regex.replace("\\$", ".+")
    # According to mutt manual "4.1 Regular Expressions" backslashes must
    # be quoted for a regular expression in initialization command
    regex = regex.replace("\\", "\\\\\\\\")
    # For some unknown reason "=" must not be escaped twice
    regex = regex.replace("\\\\=", "=")
    cmd += regex + "<enter>\""
    file_.write(cmd)
    file_.close()


def main():
    '''main function, called when script file is executed directly'''

    parser = argparse.ArgumentParser()
    parser.add_argument('vfolder',
                        help='The folder with the virtual messages')
    parser.add_argument('cmdfile',
                        help='The command file to generate')

    args = parser.parse_args()

    opt_vfolder = os.path.expanduser(args.vfolder)
    opt_cmd_file = os.path.expanduser(args.cmdfile)

    if not os.path.isdir(opt_vfolder):
        print("Could not find given vfolder")
        sys.exit(1)

    if os.path.exists(opt_cmd_file):
        os.unlink(opt_cmd_file)

    msg_id = parse_message_id(sys.stdin)
    if msg_id:
        found = False
        cmd_file_written = False
        for entry in os.listdir(os.path.join(opt_vfolder, "cur")):
            entry = os.path.join(opt_vfolder, "cur", entry)
            if os.path.islink(entry):
                file_ = open(entry, "r")
                msg_id2 = parse_message_id(file_)
                file_.close()
                if msg_id == msg_id2:
                    found = True
                    sourcefile = os.path.realpath(entry)
                    maildir = parse_maildir(sourcefile)
                    write_cmd_file(opt_cmd_file, maildir, msg_id)
                    break

        if found and cmd_file_written:
            sys.exit(0)
        else:
            if not found:
                print("Could not find given email")
            # mutt waits for key press if external command returns with code != 0
            # even if wait_key is not set. This is good for us as we want to see
            # the error messages
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
