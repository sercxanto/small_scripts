#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" paypal2homebank.py

    Convert the CSV export of paypal to homebank CSV format
"""

# The MIT License (MIT)
#
# Copyright (c) 2020 Georg Lutz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Standard library imports:
import argparse
import csv
import datetime
import logging
import sys



def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="""Convert the CSV export of paypal to homebank CSV format""")
    parser.add_argument("csvfile", help="CSV file to convert")
    parser.add_argument("outfile", help="CSV file to write to")
    return parser.parse_args()


class ParserErrorException(Exception):
    '''Exception error, parsing mismatch'''
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def format_homebank_memo(paypal_betreff, paypal_hinweis):
    '''Formats the homebank memo field with paypal betreff and hinweis'''

    memo = ""

    if paypal_betreff:
        memo = paypal_betreff
        if paypal_hinweis:
            memo += ", " + paypal_hinweis
    else:
        if paypal_hinweis:
            memo = paypal_hinweis

    return memo


def paypal2homebank(filepath, homebank_csvfile):
    '''Fix the whole CSV file, writes to outfile.

    Parameters:

    filepath: Path to the input file
    homebank_csvfile: File object to write to

    sys.exits in case of error.
    '''

    used_fieldnames_paypal = [
        "Datum",
        "Name",
        "Typ",
        "Status",
        "Währung",
        "Netto",
        "Betreff",
        "Hinweis",
        "Auswirkung auf Guthaben"]

    fieldnames_homebank = [
        "date",
        "payment",
        "info",
        "payee",
        "memo",
        "amount",
        "category",
        "tags"
    ]


    # Homebank supports only one currency for an account
    # Therefor make sure that we don't have multiple currencies in one export
    first_used_currency = None

    # "utf-8-sig": Paypal exports its CSV with byte order mark (BOM), tell python about it
    # otherwise its prepended to the first fieldname ("Datum")
    with open(filepath, "r", encoding="utf-8-sig") as filehandle:

        filereader = csv.DictReader(
            filehandle, delimiter=',', quotechar='"')

        filewriter = csv.DictWriter(
            homebank_csvfile, fieldnames=fieldnames_homebank,
            delimiter=';', quotechar='"')
        filewriter.writeheader()

        row_nr = 0

        for paypal_record in filereader:
            row_nr = row_nr + 1

            logging.info("Processing line %d", row_nr)
            if row_nr == 1:
                for fieldname in used_fieldnames_paypal:
                    if fieldname not in filereader.fieldnames:
                        logging.error(
                            "Expected field name %s not found in CSV. Stop here.", fieldname)
                        sys.exit(1)

            if paypal_record["Auswirkung auf Guthaben"] not in ["Soll", "Haben"]:
                logging.info(
                    "Skipping type %s in line %d", paypal_record["Auswirkung auf Guthaben"], row_nr)
                continue

            if first_used_currency:
                if paypal_record["Währung"] != first_used_currency:
                    logging.error("Currency mismatch in line %d", row_nr)
                    sys.exit(1)
            else:
                first_used_currency = paypal_record["Währung"]


            datum = datetime.datetime.strptime(paypal_record["Datum"], "%d.%m.%Y")
            homebank_record = {}
            homebank_record["date"] = datum.strftime("%Y-%m-%d")
            homebank_record["payment"] = 0
            homebank_record["info"] = paypal_record["Typ"]
            homebank_record["memo"] = format_homebank_memo(paypal_record["Betreff"], paypal_record["Hinweis"])
            homebank_record["payee"] = paypal_record["Name"]
            homebank_record["amount"] = paypal_record["Netto"]

            filewriter.writerow(homebank_record)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    with open(args.outfile, "w", encoding="utf-8") as outfile:
        paypal2homebank(args.csvfile, outfile)

if __name__ == "__main__":
    main()
