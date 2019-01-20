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

import datetime
import os.path
from optparse import OptionParser
import re
import smtplib
import sys

VERSIONSTRING = "0.1"


def build_test_message(email, str_):
    '''Builds the raw text for the mail message including the email receipent and a unique string'''
    msg = "From: <" + options.mailfrom + ">\n"
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

parser = OptionParser(
    usage="%prog [options] --host hostname --file filename",
    version="%prog " + VERSIONSTRING + os.linesep +
    "Copyright (C) 2009-2019 Georg Lutz <georg AT NOSPAM georglutz DOT de")

parser.add_option(
    "", "--mailfrom",
    default="",
    dest="mailfrom", help="Sets the envelope from, default to an empty string")
parser.add_option(
    "-f", "--file",
    default="",
    dest="file", help="file with mail addresses")
parser.add_option(
    "", "--host",
    dest="host", help="hostname", default="")
parser.add_option(
    "", "--port",
    dest="port", type=int, default=25,
    help="port, defaults to 25")
parser.add_option(
    "-s", "--send",
    action="store_true", dest="send", default=False,
    help="Actually send test emails, defaults to False")

(options, args) = parser.parse_args()

if (len(options.host) == 0) or (len(options.file) == 0):
    parser.print_help()
    sys.exit(2)

with open(os.path.expanduser(options.file), "r") as file_:
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
        conn = smtplib.SMTP(options.host, options.port)
    except:
        print "Cannot connect to %s:%s" % (options.host, options.port)
    sys.exit(1)

    rc = conn.docmd("HELO xyz.de")
    if rc[0] < 200 or rc[0] > 299:
        print "Error: %s" % rc[1]
    rc = conn.docmd("MAIL FROM: <" + options.mailfrom + ">")
    if rc[0] < 200 or rc[0] > 299:
        print "Error: %s" % rc[1]
    cmd = "RCPT TO: <%s>" % address
    rc = conn.docmd(cmd)
    if rc[0] < 200 or rc[0] > 299:
        print "Adress NOK: %s" % address
    else:
        print "Adress OK: %s" % address
    if options.send:
        print "Sending..."
        msg = build_test_message(address, str(i))
        i = i + 1
        rc = conn.data(msg)
        if rc[0] < 200 or rc[0] > 299:
            print "Error in data cmd: %s %s" % (rc[0], rc[1])
    conn.quit()
