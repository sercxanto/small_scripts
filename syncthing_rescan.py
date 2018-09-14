#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" syncthing_rescan.py
    Manually triggers a rescan of the local Syncthing instance"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

# The MIT License (MIT)
#
# Copyright (c) 2017 Georg Lutz
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
import os
import http.client
import xml.parsers.expat


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Manually triggers a rescan of the local Syncthing instance")

    return parser.parse_args()


def get_config():
    '''Returns a dict with the syncthing config

    { "apikey": "here is the api, key",
      "address": "the address of the GUI server"
    }
    '''
    filepath = os.path.expanduser("~/.config/syncthing/config.xml")

    result = {
        "apikey": "",
        "address": ""
    }

    # Workaround to allow write access to variables from inner functions
    in_gui = [False]
    in_address = [False]
    in_apikey = [False]


    def cb_start_element(name, attrs):
        '''expat callback'''

        if name == "gui":
            in_gui[0] = True
        if in_gui[0] and name == "address":
            in_address[0] = True
        if in_gui[0] and name == "apikey":
            in_apikey[0] = True

    def cb_end_element(name):
        '''expat callback'''

        if name == "gui" and in_gui[0]:
            in_gui[0] = False

        if name == "address" and in_address[0]:
            in_address[0] = False

        if name == "apikey" and in_apikey[0]:
            in_apikey[0] = False

    def cb_character_data_handler(data):
        '''expat callback'''

        if in_address[0]:
            result["address"] = data

        if in_apikey[0]:
            result["apikey"] = data

    with open(filepath, "rb") as filehandle:
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = cb_start_element
        parser.EndElementHandler = cb_end_element
        parser.CharacterDataHandler = cb_character_data_handler
        parser.ParseFile(filehandle)
        return result


def main():
    '''main function, called when script file is executed directly'''
    get_args()
    config = get_config()
    url = "http://" + config["address"] + "/rest/db/scan"
    print("Calling " + url + ":")

    # can't use urllib2. because it capitalizes headers, i.e. transforms
    #   request.add_header("X-API-Key", config["apikey"])
    # to
    #   request.add_header("X-Api-Key", config["apikey"])
    conn = http.client.HTTPConnection("127.0.0.1:8384")
    headers = {"X-API-Key": config["apikey"]}
    conn.request("POST", "/rest/db/scan", headers=headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()

if __name__ == "__main__":
    main()

