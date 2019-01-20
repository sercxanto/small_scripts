#!/usr/bin/python
# vim: set fileencoding=utf-8 :
'''smtpcheckaddresses.py accpepts a list of email addresses in a text file, one
line per address. For each address it then opens a connection to a given host
and checks the return code for the "RCPT TO" command. If the return code is in
the range 200 to 299 the email address is assumed to be "OK".'''
#
#    smtpcheckaddresses.py
#
#    Tests email server
#
#    Copyright (C) 2009-2019 Georg Lutz <georg AT NOSPAM georglutz DOT de>
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
import datetime
import os.path
import re
import smtplib
import sys

VERSIONSTRING = "0.1"


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Tests email server. Accepts a list of email addresses in a text\
        file, one line per address. For each address it then opens a connection to a\
        given host and checks the return code for the \"RCPT TO\" command. If the return\
        code is in the range 200 to 299 the email address is assumed to be \"OK\"")
    parser.add_argument(
        "--mailform", help="Sets the envelope from, default to an empty string",
        default="")
    parser.add_argument(
        "file",
        help="file with mail addresses")
    parser.add_argument(
        "host",
        help="hostname")
    parser.add_argument(
        "--port",
        help="port, defaults to 25",
        type=int, default=25)
    parser.add_argument(
        "--send",
        action="store_true", default=False,
        help="Actually send test emails, defaults to False")

    return parser.parse_args()


def build_test_message(email, mailfrom, str_):
    '''Builds the raw text for the mail message including the email receipent and a unique string'''
    msg = "From: <" + mailfrom + ">\n"
    msg += "To: <" + email + ">\n"
    # RFC822 date:
    msg += "Date: " + datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z") + "\n"
    msg += "User-Agent: smtpcheckaddresses.py\n"
    msg += "Subject: smtpcheckaddresses.py mail to " + email + "\n"
    msg += "\n"
    msg += "This is an automated test mail from smtpcheckaddresses.py\n"
    msg += "The identifier for this message is " + str_
    return msg

########### MAIN PROGRAM #############

args = get_args()

with open(os.path.expanduser(args.file), "r") as file_:
    line = file_.readline()
    addresses = []
    while line != "":
        line = re.sub("\n", "", line)
        # Skip empty lines
        if len(line) > 0:
            addresses.append(line)
        line = file_.readline()

i = 0
for address in addresses:
    try:
        conn = smtplib.SMTP(args.host, args.port)
    except:
        print "Cannot connect to %s:%s" % (args.host, args.port)
    sys.exit(1)

    rc = conn.docmd("HELO xyz.de")
    if rc[0] < 200 or rc[0] > 299:
        print "Error: %s" % rc[1]
    rc = conn.docmd("MAIL FROM: <" + args.mailfrom + ">")
    if rc[0] < 200 or rc[0] > 299:
        print "Error: %s" % rc[1]
    cmd = "RCPT TO: <%s>" % address
    rc = conn.docmd(cmd)
    if rc[0] < 200 or rc[0] > 299:
        print "Adress NOK: %s" % address
    else:
        print "Adress OK: %s" % address
    if args.send:
        print "Sending..."
        msg = build_test_message(address, args.mailfrom, str(i))
        i = i + 1
        rc = conn.data(msg)
        if rc[0] < 200 or rc[0] > 299:
            print "Error in data cmd: %s %s" % (rc[0], rc[1])
    conn.quit()
