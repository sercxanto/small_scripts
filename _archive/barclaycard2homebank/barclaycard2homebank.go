// The MIT License (MIT)
//
// Copyright (c) 2020 Georg Lutz
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
	"errors"
	"fmt"
	"log"
	"os"
	"reflect"
	"strconv"
	"strings"
	"time"

	"github.com/alecthomas/kong"
	"github.com/xuri/excelize/v2"
)

var CLI struct {
	Infile  string `arg:"" name:"infile" help:"Excel file downloaded from barclaycard website" type:"path"`
	Outfile string `arg:"" name:"outfile" help:"CSV file ready to import into homebank" type:"path"`
}

// Single record of barclaycard data, all data is stored as string in the the excel file
type BarclaycardRecord struct {
	transactionDate string
	bookingDate     string
	value           string
	description     string
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
func convertRecord(barclaycardRecord *BarclaycardRecord) (record HomebankRecord, err error) {
	var result HomebankRecord
	date, err := time.Parse("02.01.2006", barclaycardRecord.transactionDate)
	if err != nil {
		return result, errors.New("Date parsing error")
	}
	result.date = date.Format("2006-01-02")
	result.payment = 1 // Credit card
	result.info = barclaycardRecord.description
	// Format in excel export is "3,14 €"
	amountString := strings.Replace(barclaycardRecord.value, ",", ".", -1)
	amountString = strings.TrimRight(amountString, "€")
	result.amount, err = strconv.ParseFloat(strings.TrimSpace(amountString), 64)
	if err != nil {
		return result, err
	}
	return result, nil
}

// main logic
// Converts excel file to CSV file
// Returns true on success, false otherwise
func barclaycard2homebank(infilePath string, outfilePath string) bool {
	log.Println("infile", infilePath)
	log.Println("outfile", outfilePath)

	f, err := excelize.OpenFile(infilePath)
	if err != nil {
		log.Println(err)
		return false
	}

	rows, err := f.GetRows("Sheet1")
	if err != nil {
		log.Println(err)
		return false
	}

	dataHeader := []string{
		"Referenznummer",
		"Buchungsdatum", // eigentlich: Transaktionsdatum
		"Buchungsdatum",
		"Betrag",
		"Beschreibung",
		"Typ",
		"Status",
		"Kartennummer",
		"Originalbetrag",
		"Mögliche Zahlpläne",
		"Land",
		"Name des Karteninhabers",
		"Kartennetzwerk",
		"Kontaktlose Bezahlung",
	}

	inDataSection := false

	var homebankRecords []HomebankRecord

	for lineNr, row := range rows {
		if inDataSection {
			barclaycardRecord := BarclaycardRecord{
				transactionDate: row[1],
				bookingDate:     row[2],
				value:           row[3],
				description:     row[4],
			}
			log.Println("Processing line", lineNr)
			homebankRecord, err := convertRecord(&barclaycardRecord)
			if err != nil {
				log.Println("Parsing error in line", lineNr)
				log.Printf("Error: %s", err)
				return false
			}
			homebankRecords = append(homebankRecords, homebankRecord)
		}
		if reflect.DeepEqual(row, dataHeader) {
			log.Println("Header found in line", lineNr)
			inDataSection = true
		}
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
			rec.date, rec.payment, rec.payee, rec.info, rec.memo, rec.amount, rec.category, rec.tags)
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

	kong.Parse(&CLI,
		kong.Description("Converts an barclaycard excel file to a homebank CSV file"))

	result := barclaycard2homebank(CLI.Infile, CLI.Outfile)
	if result {
		os.Exit(0)
	}
	os.Exit(1)
}
