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
	"bytes"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"testing"
)

// Creates a named temporary file
func createTempFile() (name string, err error) {
	tmpFile, err := ioutil.TempFile("", "moneywallet2homebank_test-")
	if err != nil {
		return "", errors.New("Cannot create temporary file")
	}
	outfilePath := tmpFile.Name()
	tmpFile.Close()
	return outfilePath, nil
}

func TestIsValidMoneyWalletHeader(t *testing.T) {

	header_ok := []string{
		"wallet",
		"currency",
		"category",
		"datetime",
		"money",
		"description",
	}

	header_nok := []string{
		"wallet",
		"currency",
		"category",
		"datetime",
		"money",
		"description xxx",
	}

	header_wrong_length := []string{
		"wallet",
		"currency",
		"category",
		"datetime",
		"money",
	}

	result := isValidMoneyWalletHeader(header_ok)
	if !result {
		t.Error("isValidMoneyWalletHeader returned false")
	}

	result = isValidMoneyWalletHeader(header_nok)
	if result {
		t.Error("isValidMoneyWalletHeader returned true")
	}

	result = isValidMoneyWalletHeader(header_wrong_length)
	if result {
		t.Error("isValidMoneyWalletHeader returned false")
	}

}

func TestMoneywallet2Homebank(t *testing.T) {
	infilePath := path.Join("testfiles", "MoneyWallet_export_1.csv")
	expectedPath := path.Join("testfiles", "converted_1.csv")
	outfilePath, err := createTempFile()
	if err != nil {
		t.Error("Cannot create tempfile")
	}

	fmt.Println("Temporary file: ", outfilePath)

	result := moneywallet2homebank(infilePath, outfilePath)
	if !result {
		t.Error("moneywallet2homebank returned error")
	}

	calculated, err := ioutil.ReadFile(outfilePath)
	if err != nil {
		t.Errorf("Cannot read file %s", outfilePath)
	}
	expected, err := ioutil.ReadFile(expectedPath)
	if err != nil {
		t.Errorf("Cannot read file %s", outfilePath)
	}

	if same := bytes.Equal(calculated, expected); !same {
		t.Error("CSV file does not match expectation")
	}

	os.Remove(outfilePath)
}
