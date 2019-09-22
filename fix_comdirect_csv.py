#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" fix_comdirect_csv.py

    Fix the CSV export of comdirect bank"""

# The MIT License (MIT)
#
# Copyright (c) 2019 Georg Lutz
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



def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Fix the CSV export of comdirect")
    parser.add_argument(
        "csvfile",
        help="CSV file to fix")
    parser.add_argument(
        "output_file",
        help="CSV file to write to")
    parser.add_argument(
        "--output_format",
        help="The CSV output format",
        choices=["homebank"],
        default="homebank")
    return parser.parse_args()


class ParserErrorException(Exception):
    '''Exception error, parsing mismatch'''
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def parse_csv_date(date_string):
    '''Parses the CSV date as used by comdirect, returns python datetime object

    If no valid date could be found, return None
    '''
    try:
        timestamp = datetime.datetime.strptime(date_string, "%d.%m.%Y")
        return datetime.date(timestamp.year, timestamp.month, timestamp.day)
    except ValueError:
        return None



def split_buchungstext(list_of_fields, buchungstext):
    '''Split buchungstext according to list_of_fields

    Example:

    list_of_fields: ["first", "second", "third"]
    buchungstext: "first:abcfirstsecond:abcsecond third:abcthird"

    Result:

    {
        "first": "abcfirst",
        "second": "abcsecond",
        "third": "abcthird"
    }
    '''

    # Store the found fieldnames in the following dict:
    #
    # * key: start of where field has been found
    # * value: name of the field,
    #
    # e.g.:
    # {
    #      0: "first",
    #     14: "second",
    #     31: "third"
    # }
    field_start_positions = {}
    for field_name in list_of_fields:
        pos = buchungstext.find(field_name + ":")
        if pos >= 0:
            field_start_positions[pos] = field_name

    stop_loop = False
    iterator = iter(sorted(field_start_positions))

    try:
        field_start_position = next(iterator)
    except StopIteration:
        stop_loop = True

    result = {}

    while not stop_loop:
        field_name = field_start_positions[field_start_position]
        value_start_position = field_start_position + len(field_name) + 1
        try:
            field_start_position = next(iterator)
            value_end_position = field_start_position
        except StopIteration:
            stop_loop = True
            value_end_position = len(buchungstext)
        value = buchungstext[value_start_position:value_end_position].strip()
        result[field_name] = value

    return result


def get_first_n_words(number, text):
    '''Return the first n space seperated words from a text'''
    return " ".join(text.split(" ")[0:number])


def convert_umsatz(umsatz):
    '''Convert umsatz numbers to float

    Paramters:

    umsatz: Umsatz as in the CSV file as string

    umsatz has "," as decimal seperator and "." as thousand seperator
    '''
    return float(umsatz.replace(".", "").replace(",", "."))


def convert_record_to_internal(in_record):
    '''Convert a single record from in_record to internal format

    Parameters:

    in_record: dict corresponding to the CSV produced by comdirect, like the following:

        {
            "buchungstag": "05.08.2019",
            "valuta": "05.08.2019",
            "vorgang": "Übertrag/Überweisung",
            "buchungstext": "Auftraggeber:auftragnameBuchungstext: Der Buchungstext 123 456
            Empfänger:empfängernameEmpfänger: nameKto/IBAN: DE123 BLZ/BIC: ABC123",
            "umsatz": "-139.40"
        }

    out_record: sanitized CSV output:

        {
            "date": python datetime.date object,
            "valuta": python datetime.date object,
            "initiator": "auftragname",
            "payee":
                {
                    "name": "empfängername",
                    "account_id": "DE123",
                    "bic": "ABC123"
                },
            "info": "first three space seperated words of buchungstext",
            "memo": "the full buchungstext",
            "amount": 12.34,
        }

    If some field cannot be assigned it is set to None
    '''

    out_record = {}

    # Simple part:
    out_record["date"] = parse_csv_date(in_record["buchungstag"])
    out_record["valuta"] = parse_csv_date(in_record["valuta"])
    out_record["amount"] = convert_umsatz(in_record["umsatz"])
    out_record["memo"] = in_record["buchungstext"]

    # Split fields:
    list_of_fields = [
        "Auftraggeber", "Buchungstext", "Empfänger", "Kto/IBAN", "BLZ/BIC"]
    split_info = split_buchungstext(list_of_fields, in_record["buchungstext"])

    out_record["initiator"] = split_info.get("Auftraggeber")

    if "Buchungstext" in split_info:
        out_record["info"] = get_first_n_words(3, split_info["Buchungstext"])
    if "Empfänger" in split_info:
        out_record["payee"] = {}
        out_record["payee"]["name"] = split_info["Empfänger"]
        if "Kto/IBAN" in split_info:
            out_record["payee"]["account_id"] = split_info["Kto/IBAN"]
        if "BLZ/BIC" in split_info:
            out_record["payee"]["bic"] = split_info["BLZ/BIC"]
    else:
        if out_record["amount"] < 0:
            if out_record["initiator"]:
                # For "Lastschrift" there is no "Empfänger", but a "Auftraggeber" in the CSV
                out_record["payee"] = {}
                out_record["payee"]["name"] = out_record["initiator"]
                out_record["payee"]["account_id"] = None
                out_record["payee"]["bic"] = None
            else:
                # For "Kartenverfügung" there is no "Empfänger" set, but usually the payee encoded
                # in the buchungstext
                if in_record["vorgang"] == "Kartenverfügung":
                    out_record["payee"] = {}
                    out_record["payee"]["name"] = get_first_n_words(4, split_info["Buchungstext"])
                    out_record["payee"]["account_id"] = None
                    out_record["payee"]["bic"] = None
    return out_record


def convert_internal_to_homebank(in_record):
    '''Convert from internal format to homebank format

    Parameters:

    in_record: The internal record format, see convert_record_to_internal

    Result:

    The python dict represantation of homebanks CSV format

    See http://homebank.free.fr/help/misc-csvformat.html
    '''

    if not in_record["date"]:
        return None

    homebank = {}
    homebank["date"] = in_record["date"].strftime("%Y-%m-%d")
    homebank["payment"] = 0
    homebank["info"] = in_record["info"]
    if "payee" in in_record:
        homebank["payee"] = in_record["payee"]["name"]
    homebank["memo"] = in_record["memo"]
    homebank["amount"] = str(in_record["amount"])
    homebank["category"] = ""
    homebank["tags"] = ""
    return homebank


def convert_row_to_record(row):
    '''Converts a single CSV row to a record
    '''
    record = {}
    record["buchungstag"] = row[0]
    record["valuta"] = row[1]
    record["vorgang"] = row[2]
    record["buchungstext"] = row[3]
    record["umsatz"] = row[4]
    return record


def fix_file(filepath, output_format, outfile):
    '''Fix the whole CSV file, writes to outfile.

    Parameters:

    filepath: Path to the input file
    output_format: The format of the output CSV file
    outfile: A file handle for the output file
    '''

    expected_header = [
        "Buchungstag", "Wertstellung (Valuta)", "Vorgang", "Buchungstext", "Umsatz in EUR", ""]

    with open(filepath, "r", encoding="iso-8859.1") as filehandle:
        filereader = csv.reader(filehandle, delimiter=";")
        fieldnames = ["date", "payment", "info", "payee", "memo", "amount", "category", "tags"]
        filewriter = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
        filewriter.writeheader()
        row_nr = 0
        in_data = False

        for row in filereader:
            row_nr = row_nr + 1
            if not in_data and row == expected_header:
                logging.info("Found header in line %d", row_nr)
                in_data = True
            elif in_data:
                if row:
                    logging.info("Processing line %d", row_nr)
                    in_record = convert_row_to_record(row)
                    internal_record = convert_record_to_internal(in_record)
                    homebank_record = convert_internal_to_homebank(internal_record)
                    if homebank_record:
                        filewriter.writerow(homebank_record)
                    else:
                        logging.info("Skipping entry in line %d", row_nr)
                else:
                    logging.info("Empty line in %d. Exiting data section.", row_nr)
                    in_data = False


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    output_file = open(args.output_file, "w")
    fix_file(args.csvfile, args.output_format, output_file)

if __name__ == "__main__":
    main()
