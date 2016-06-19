#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" fix_fiducia_csv.py

    Fix the CSV export of fiducia driven banking websites"""

# The MIT License (MIT)
#
# Copyright (c) 2016 Georg Lutz
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
import sys


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Fix the CSV export of fiducia driven banking websites")
    parser.add_argument("csvfile", help="CSV file to fix")
    return parser.parse_args()


class ParserErrorException(Exception):
    '''Exception when we detect a file not belonging to duplicity'''
    pass


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


def fix_file(filepath, outfile):
    '''Fix the whole CSV file, writes to outfile'''
    skip_lines = 12
    expected_header = ["Buchungstag", "Valuta", "Auftraggeber/Zahlungsempfänger", \
            "Empfänger/Zahlungspflichtiger", "Konto-Nr.", "IBAN", "BLZ", "BIC", \
            "Vorgang/Verwendungszweck", "Kundenreferenz", "Währung", "Umsatz", " "]
    with open(filepath, "rb") as filehandle:
        filereader = csv.reader(filehandle, delimiter=";")
        filewriter = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_ALL)
        row_nr = 0

        for row in filereader:
            row_nr = row_nr + 1

            if row_nr <= skip_lines:
                continue

            row = [x.decode("iso-8859.1").encode("utf8") for x in row]

            if row_nr == skip_lines + 1:
                if row != expected_header:
                    raise ParserErrorException(filepath)
                # Don't know the meaning of the empty last field of the header
                row[-1] = "unknown"

            # Stop on first empty line: We are at the end of data
            if len(row) == 0:
                break

            row[8] = fix_multilinenote(row[8])

            filewriter.writerow(row)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    fix_file(args.csvfile, sys.stdout)

if __name__ == "__main__":
    main()
