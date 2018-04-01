#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" fix_fiducia_csv.py

    Fix the CSV export of fiducia driven banking websites"""

# The MIT License (MIT)
#
# Copyright (c) 2016-2018 Georg Lutz
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
import datetime
import csv
import sys


def valid_date(date_):
    '''Date validation for argparse'''
    try:
        return datetime.datetime.strptime(date_, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_)
        raise argparse.ArgumentTypeError(msg)


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Fix the CSV export of fiducia driven banking websites")
    parser.add_argument("csvfile", help="CSV file to fix")
    parser.add_argument(
        "--mappingfile",
        help="CSV file for simple search pattern matching.\
              If given, a column \'account\' and \'description\' with the mapped string will be\
              added to the output")
    parser.add_argument(
        "--startdate",
        help="Only take into account records that are younger that the given date.\
              An ISO8601 format is expected, e.g. 2018-01-01",
        type=valid_date)
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


def read_mapping(filepath):
    '''Reads a mapping file and returns a structure

    The file is supposed to be in CSV format:
    * the delimiter is the semicolon, without any quoting
    * the first line must contain the row names "account;description;searchterm1;searchterm2"
    * account is the destination account name in gnucash
    * description is the description for the transaction
    * searchterm1 is used for simple text search in all rows of the input data
    * searchtem2 may be empty. If non empty this is the second string which the
      input data is searched for
        * for a sucessfull match searchterm1 AND searchterm2 must be matched

    Example:
        account;description;searchterm1;seachterm2
        account:name;resulting text;search one;search two

    The mapping is returned as dict:

    {
        'searchterm1': ['string1', 'string12'],
        'searchterm2': ['string2', ''],
        'description': ['text', 'text2']
        'account' : ['accountname1', 'accountname2']
    }

    In case of any error an exception is thrown.
    '''
    result = {
        "account": [],
        "description": [],
        "searchterm1": [],
        "searchterm2": []
        }
    expected_header = ["account", "description", "searchterm1", "searchterm2"]

    if filepath is None or len(filepath) == 0:
        return result
    with open(filepath, "rb") as filehandle:
        filereader = csv.reader(filehandle, delimiter=";")
        row_nr = 0
        for row in filereader:
            row_nr = row_nr + 1
            if row_nr == 1:
                if row != expected_header:
                    raise ParserErrorException(filepath)
            else:
                print row
                if len(row) < 3 or len(row) > 4:
                    raise ParserErrorException(filepath + ", line " + str(row_nr))
                if len(row[0]) == 0:
                    raise ParserErrorException(filepath + ", line " + str(row_nr))
                if len(row[1]) == 0:
                    raise ParserErrorException(filepath + ", line " + str(row_nr))
                if len(row[2]) == 0:
                    raise ParserErrorException(filepath + ", line " + str(row_nr))
                result["account"].append(row[0])
                result["description"].append(row[1])
                result["searchterm1"].append(row[2])
                if len(row) > 3:
                    result["searchterm2"].append(row[3])
                else:
                    result["searchterm2"].append("")
        if row_nr == 0:
            raise ParserErrorException(filepath)
    return result


def get_mapped_text(row, mapping):
    '''Returns an array with the account and description for a given row and a mapping.

    row: a single line, an array of strings
    mapping: see read_mapping

    Returns None in case of not found
    '''
    result = None

    for i_mapping in range(len(mapping["account"])):
        nr_matches = 0
        nr_matches_needed = 1
        if len(mapping["searchterm2"][i_mapping]) > 0:
            nr_matches_needed = 2
        for field in row:
            if field.find(mapping["searchterm1"][i_mapping]) >= 0:
                nr_matches = nr_matches + 1
            if len(mapping["searchterm2"][i_mapping]) > 0:
                if field.find(mapping["searchterm2"][i_mapping]) >= 0:
                    nr_matches = nr_matches + 1
            if nr_matches >= nr_matches_needed:
                break
        if nr_matches >= nr_matches_needed:
            result = [mapping["account"][i_mapping], mapping["description"][i_mapping]]
            break
    return result


def fix_file(filepath, mapping_file_path, start_date, outfile):
    '''Fix the whole CSV file, writes to outfile.

    filepath: Path to the input file
    mapping_file_path: Path to the mapping file. If != None the fields account and description
    are added to the outfile
    start_date: Datetime object. If != None only return records that whose date is >= startdate'''
    skip_lines = 12
    expected_header = ["Buchungstag", "Valuta", "Auftraggeber/Zahlungsempfänger", \
            "Empfänger/Zahlungspflichtiger", "Konto-Nr.", "IBAN", "BLZ", "BIC", \
            "Vorgang/Verwendungszweck", "Kundenreferenz", "Währung", "Umsatz", " "]
    mapping = None
    if mapping_file_path != None:
        mapping = read_mapping(mapping_file_path)

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
                # Empty last field has the meaning of (S)oll/(H)aben
                # We will put the info into Umsatz and overwrite it with
                # the ISO8601 version of the Buchungstag
                row[-1] = "Buchungstag ISO8601"
                if mapping != None:
                    row.append("Account")
                    row.append("Description")
            else:
                # Stop on first empty line: We are at the end of data
                if len(row) == 0:
                    break

                buchungstag = datetime.datetime.strptime(row[0], "%d.%m.%Y")
                if start_date != None and buchungstag < start_date:
                    continue

                # Put (S)oll/(H)aben info as sign into Umsatz
                if row[-1] == "S":
                    row[-2] = "-" + row[-2]
                elif row[-1] == "H":
                    pass
                else:
                    raise ParserErrorException(filepath)

                row[-1] = buchungstag.strftime("%Y-%m-%d")
                row[8] = fix_multilinenote(row[8])
                if mapping != None:
                    mapped_text = get_mapped_text(row, mapping)
                    if mapped_text != None:
                        row.append(mapped_text[0])
                        row.append(mapped_text[1])
                    else:
                        row.append("")
                        row.append("")

            filewriter.writerow(row)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    fix_file(args.csvfile, args.mappingfile, args.startdate, sys.stdout)

if __name__ == "__main__":
    main()
