#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
'''smtpcheckaddresses.py accpepts a list of email addresses in a text file, one
line per address. For each address it then opens a connection to a given host
and checks the return code for the "resultPT TO" command. If the return code is in
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
#    MEresultHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import email.mime.text
import smtplib


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Tests email server. Accepts a list of email addresses in a text\
        file, one line per address. For each address it then opens a connection to a\
        given host and checks the return code for the \"resultPT TO\" command. If the return\
        code is in the range 200 to 299 the email address is assumed to be \"OK\"")
    parser.add_argument(
        "--mailfrom", help="Sets the envelope from, default to an empty string",
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


def build_test_message(mailto, mailfrom, str_):
    '''Builds the raw text for the mail message including the email receipent and a unique string'''
    msg = email.mime.text.MIMEText(
        "This is an automated test mail from smtpcheckaddresses.py\n"
        "The identifier for this message is " + str_)

    msg["From"] = email.utils.formataddr(("", mailfrom))
    msg["To"] = email.utils.formataddr(("", mailto))
    msg["Date"] = email.utils.formatdate()
    msg["User-Agent"] = "smtpcheckaddresses.py"
    msg["Subject"] = "smtpcheckaddresses.py mail to " + mailto
    return msg.as_string()


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()

    addresses = [line.rstrip('\n') for line in open(args.file, "r")]
    addresses = [x for x in addresses if len(x) > 0]

    i = 0
    for address in addresses:
        with smtplib.SMTP(args.host, args.port) as conn:
            result = conn.docmd("HELO xyz.de")
            if result[0] < 200 or result[0] > 299:
                print("Error: %s" % result[1])
            result = conn.docmd("MAIL FROM: <" + args.mailfrom + ">")
            if result[0] < 200 or result[0] > 299:
                print("Error: %s" % result[1])
            cmd = "RCPT TO: <%s>" % address
            result = conn.docmd(cmd)
            if result[0] < 200 or result[0] > 299:
                print("Adress NOK: %s" % address)
            else:
                print("Adress OK: %s" % address)
            if args.send:
                print("Sending...")
                msg = build_test_message(address, args.mailfrom, str(i))
                i = i + 1
                result = conn.data(msg)
                if result[0] < 200 or result[0] > 299:
                    print("Error in data cmd: %s %s" % (result[0], result[1]))

if __name__ == "__main__":
    main()
