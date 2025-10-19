// The MIT License (MIT)
//
// Copyright (c) 2021 Georg Lutz
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

package main

import (
	"encoding/csv"
	"errors"
	"fmt"
	"log"
	"os"
	"reflect"
	"strconv"
	"strings"
	"time"
)

func usage() {
	usage := `moneywallet2homebank

Converts an moneywallet CSV file to a homebank CSV file

For moneywallet see https://github.com/AndreAle94/moneywallet.

Usage:
	moneywallet2homebank infile outfile
	moneywallet2homebank -h

Arguments:
	infile: CSV export of moneywallet file downloaded from barclaycard website
	outfile: CSV file ready to import into homebank

Options:
	-h --help     Show this screen.`
	fmt.Println(usage)
}

// Single record of moneywallet data, all data is stored as quoted string in the CSV file
type MoneywalletRecord struct {
	wallet      string
	currency    string
	category    string
	datetime    string
	money       string
	description string
}

// See http://homebank.free.fr/help/misc-csvformat.html, format transaction
type HomebankRecord struct {
	date     string
	payment  int8
	info     string
	payee    string
	memo     string
	amount   float64
	category string
	tags     string
}

// convertRecord converts a single record from barclaycard to homebank format
func convertRecord(moneywalletRecord *MoneywalletRecord) (record HomebankRecord, err error) {
	var result HomebankRecord

	result.category = moneywalletRecord.category
	result.payment = 0
	result.info = moneywalletRecord.description
	date, err := time.Parse("2006-01-02 15:04:05", moneywalletRecord.datetime)
	if err != nil {
		return result, errors.New("Date parsing error")
	}
	result.date = date.Format("2006-01-02")
	amountString := strings.Replace(moneywalletRecord.money, ",", ".", -1)
	result.amount, err = strconv.ParseFloat(strings.TrimSpace(amountString), 64)
	if err != nil {
		return result, err
	}

	return result, nil
}

func isValidMoneyWalletHeader(record []string) bool {

	expected := []string{
		"wallet",
		"currency",
		"category",
		"datetime",
		"money",
		"description",
	}
	if reflect.DeepEqual(record, expected) {
		return true
	}
	return false
}

// main logic
// Converts moneywallet CSV file to homebank CSV file
// Returns true on success, false otherwise
func moneywallet2homebank(infilePath string, outfilePath string) bool {
	log.Println("infile", infilePath)
	log.Println("outfile", outfilePath)

	infile, err := os.Open(infilePath)
	if err != nil {
		log.Fatalln("Cannot open input file", err)
	}
	csvReader := csv.NewReader(infile)
	inRecords, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal("Cannot parse input file", err)
	}

	if len(inRecords) == 0 {
		log.Fatal("Cannot parse input file")
	}

	if !isValidMoneyWalletHeader(inRecords[0]) {
		log.Fatal("No valid CSV header found")
	}

	var homebankRecords []HomebankRecord

	for recordNr, row := range inRecords[1:] {
		moneyWalletRecord := MoneywalletRecord{
			wallet:      row[0],
			currency:    row[1],
			category:    row[2],
			datetime:    row[3],
			money:       row[4],
			description: row[5],
		}
		log.Println("Processing line", recordNr+1)
		homebankRecord, err := convertRecord(&moneyWalletRecord)
		if err != nil {
			log.Println("Parsing error in line", recordNr+1)
			return false
		}
		homebankRecords = append(homebankRecords, homebankRecord)
	}

	outfile, err := os.Create(outfilePath)
	if err != nil {
		log.Println(err)
		return false
	}
	defer outfile.Close()

	log.Println("Writing to file", outfilePath)
	for _, rec := range homebankRecords {
		line := fmt.Sprintf("%s;%d;%s;%s;%s;%f;%s;%s",
			rec.date, rec.payment, rec.info, rec.payee, rec.memo, rec.amount, rec.category, rec.tags)
		_, err := fmt.Fprintln(outfile, line)
		if err != nil {
			log.Println(err)
			return false
		}
	}

	return true
}

func main() {

	log.SetFlags(log.Lshortfile)

	if len(os.Args) == 2 {
		usage()
		os.Exit(0)
	}

	if len(os.Args) != 3 {
		usage()
		os.Exit(1)
	}

	infile := os.Args[1]
	outfile := os.Args[2]

	result := moneywallet2homebank(infile, outfile)
	if result {
		os.Exit(0)
	}
	os.Exit(1)
}
