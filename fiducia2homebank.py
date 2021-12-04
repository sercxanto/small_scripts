#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" fiducia2homebank.py

    Convert the CSV export of fiducia driven banking websites,
    i.e. Volksbank to homebank CSV format"""

# The MIT License (MIT)
#
# Copyright (c) 2020-2021 Georg Lutz
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
import collections
import csv
import datetime
import logging


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="""Convert the CSV export of fiducia driven banking websites,
        i.e. Volksbank to homebank csv format""")
    parser.add_argument("csvfile", help="CSV file to convert")
    parser.add_argument("outfile", help="CSV file to write to")
    return parser.parse_args()


class ParserErrorException(Exception):
    '''Exception error, parsing mismatch'''
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def fix_multilinenote(in_note):
    '''Fixes the newlines in the note field'''
    out_note = ""
    first_newline = True

    for char in in_note:
        if char == "\n":
            if first_newline:
                out_note = out_note + " "
                first_newline = False
            else:
                pass
        else:
            out_note = out_note + char

    return out_note


def fiducia2homebank(filepath, homebank_csvfile):
    '''Fix the whole CSV file, writes to outfile.

    Parameters:

    filepath: Path to the input file
    homebank_csvfile: File object to write to
    '''

    fieldnames_fiducia = [
        "buchungstag",
        "valuta",
        "textschluessel",
        "primanota",
        "zahlungsempfaenger",
        "zahlungsempfaenger_kto",
        "zahlungsempfaenger_iban",
        "zahlungsempfaenger_blz",
        "zahlungsempfaenger_bic",
        "verwendungszweck",
        "kundenreferenz",
        "waehrung",
        "umsatz",
        "habensoll"
    ]

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

    expected_header = collections.OrderedDict([
        ("buchungstag", "Buchungstag"),
        ("valuta", "Valuta"),
        ("textschluessel", "Textschlüssel"),
        ("primanota", "Primanota"),
        ("zahlungsempfaenger", "Zahlungsempfänger"),
        ("zahlungsempfaenger_kto", "ZahlungsempfängerKto"),
        ("zahlungsempfaenger_iban", "ZahlungsempfängerIBAN"),
        ("zahlungsempfaenger_blz", "ZahlungsempfängerBLZ"),
        ("zahlungsempfaenger_bic", "ZahlungsempfängerBIC"),
        ("verwendungszweck", "Vorgang/Verwendungszweck"),
        ("kundenreferenz", "Kundenreferenz"),
        ("waehrung", "Währung"),
        ("umsatz", "Umsatz"),
        ("habensoll", "Soll/Haben")])

    with open(filepath, "r", encoding="iso-8859.1") as filehandle:

        filereader = csv.DictReader(
            filehandle, fieldnames=fieldnames_fiducia,
            delimiter=';', quotechar='"')

        filewriter = csv.DictWriter(
            homebank_csvfile, fieldnames=fieldnames_homebank,
            delimiter=';', quotechar='"')

        row_nr = 0
        in_data_section = False

        for fiducia_record in filereader:
            row_nr = row_nr + 1

            if not in_data_section and fiducia_record == expected_header:
                logging.info("Found header in line %d", row_nr)
                in_data_section = True
                continue
            elif in_data_section and \
                fiducia_record["primanota"] == "" and fiducia_record["zahlungsempfaenger"] == "":
                logging.info("Data section ends in line %d", row_nr)
                in_data_section = False
                break

            if not in_data_section:
                continue

            buchungstag = datetime.datetime.strptime(fiducia_record["buchungstag"], "%d.%m.%Y")
            homebank_record = {}
            homebank_record["date"] = buchungstag.strftime("%Y-%m-%d")
            homebank_record["payment"] = 0
            homebank_record["memo"] = fix_multilinenote(fiducia_record["verwendungszweck"])
            homebank_record["payee"] = fiducia_record["zahlungsempfaenger"]
            homebank_record["amount"] = fiducia_record["umsatz"]
            if fiducia_record["habensoll"] == "S":
                homebank_record["amount"] = "-" + homebank_record["amount"]

            filewriter.writerow(homebank_record)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    with open(args.outfile, "w", encoding="utf-8") as outfile:
        fiducia2homebank(args.csvfile, outfile)

if __name__ == "__main__":
    main()
