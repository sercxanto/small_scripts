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


def fiducia2homebank(filepath, homebank_csvfile):
    '''Fix the whole CSV file, writes to outfile.

    Parameters:

    filepath: Path to the input file
    homebank_csvfile: File object to write to
    '''

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
        ("bezeichnung_auftragskonto", "Bezeichnung Auftragskonto"),
        ("iban_auftragskonto", "IBAN Auftragskonto"),
        ("bic_auftragskonto", "BIC Auftragskonto"),
        ("bankname_auftragskonto", "Bankname Auftragskonto"),
        ("buchungstag", "Buchungstag"),
        ("valutadatum", "Valutadatum"),
        ("name_zahlungsbeteiligter", "Name Zahlungsbeteiligter"),
        ("iban_zahlungsbeteiligter", "IBAN Zahlungsbeteiligter"),
        ("bic_zahlungsbeteiligter", "BIC (SWIFT-Code) Zahlungsbeteiligter"),
        ("buchungstext", "Buchungstext"),
        ("verwendungszweck", "Verwendungszweck"),
        ("betrag", "Betrag"),
        ("waehrung", "Waehrung"),
        ("saldo_nach_buchung", "Saldo nach Buchung"),
        ("bemerkung", "Bemerkung"),
        ("kategorie", "Kategorie"),
        ("steuerrelevant", "Steuerrelevant"),
        ("glaebiger_id", "Glaeubiger ID"),
        ("mandatsreferenz", "Mandatsreferenz")])

    fieldnames_fiducia = list(expected_header.keys())

    with open(filepath, "r", encoding="utf-8") as filehandle:

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

            if not in_data_section:
                if fiducia_record == expected_header:
                    logging.info("Found header in line %d", row_nr)
                else:
                    logging.error("Header does not match")
                    return
                in_data_section = True
                continue

            logging.info("Processing line %d", row_nr)
            buchungstag = datetime.datetime.strptime(fiducia_record["buchungstag"], "%d.%m.%Y")
            homebank_record = {}
            homebank_record["date"] = buchungstag.strftime("%Y-%m-%d")
            homebank_record["payment"] = 0
            homebank_record["memo"] = fiducia_record["verwendungszweck"]
            homebank_record["payee"] = fiducia_record["name_zahlungsbeteiligter"]
            homebank_record["amount"] = fiducia_record["betrag"]

            filewriter.writerow(homebank_record)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    with open(args.outfile, "w", encoding="utf-8") as outfile:
        fiducia2homebank(args.csvfile, outfile)

if __name__ == "__main__":
    main()
