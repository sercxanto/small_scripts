#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" msmtpq_notify.py

    Notifies desktop user if msmtpq has actually sent or enqueued mail"""
from __future__ import print_function
#
#    Copyright (C) 2011 Georg Lutz <georg AT NOSPAM georglutz DOT de>
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

import os
import subprocess
import sys


def debug_print(text):
    '''Print out debug messages when called as msmtpq_notify_debug.py (e.g. per symlink)'''
    if os.path.basename(sys.argv[0]) == "msmtpq_notify_debug.py":
        print(text)


def get_nr_of_entries_in_queue():
    '''Returns the nr of entries in queue as an result of an call to "msmptq -d".
       -1 means error in call of msmtpq.'''
    result = -1
    try:
        proc = subprocess.Popen(
            args=" -d", executable="msmtpq", stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except:
        return result
    os.waitpid(proc.pid, 0)

    result = 0
    for line in proc.stdout:
        if line.find("  mail id = [ ") == 0:
            result += 1
    return result


def notify(text):
    '''Sends text message to desktop'''
    debug_print("notify: " + "\"" + text + "\"")
    proc = subprocess.Popen(
        "notify-send msmtpq_notify \"" + text + "\"", stderr=subprocess.PIPE,
        stdout=subprocess.PIPE, shell=True)
    for line in proc.stderr:
        line = line.strip(os.linesep)
        debug_print("Error notify-send: " + line)


def call_msmtpq():
    '''Calls msmtpQ and returns its exit code.
    Note that a call to msmtpQ also runs the queue automatically.'''
    result = -1
    args = ["msmtpQ"]
    if len(sys.argv) > 1:
        args += sys.argv[1:]
    try:
        proc = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return result
    for line in sys.stdin:
        proc.stdin.write(line)
    proc.communicate()
    result = proc.returncode
    return result



########### MAIN PROGRAM #############

if __name__ == "__main__":
    NR_OF_ENTRIES_BEFORE = get_nr_of_entries_in_queue()
    if NR_OF_ENTRIES_BEFORE < 0:
        notify("Error in calling msmtpq. Is it installed?")
        sys.exit(2)

    RETURN_CODE = call_msmtpq()
    if RETURN_CODE < 0:
        notify("Error in calling msmtpQ. Is it installed?")
        sys.exit(2)

    NR_OF_ENTRIES_AFTER = get_nr_of_entries_in_queue()
    if NR_OF_ENTRIES_AFTER < 0:
        notify("Error in calling msmtpq. Check installation!")
        sys.exit(2)

    if NR_OF_ENTRIES_BEFORE == 0 and NR_OF_ENTRIES_AFTER == 0:
        notify("Sucessfully send message.")
    else:
        notify("Messages in queue: %d." % (NR_OF_ENTRIES_AFTER))

    sys.exit(RETURN_CODE)


