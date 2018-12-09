#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" syncthing_findconflicts.py
    Scans all folders of the local Syncthing instance for conflict files"""

# The MIT License (MIT)
#
# Copyright (c) 2017-2018 Georg Lutz
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
import xml.parsers.expat


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Scans all folders of the local Syncthing instance for conflict files")
    parser.add_argument(
        "-q", "--quiet",
        help="Generates output only when conflicts are found",
        action="store_true")
    return parser.parse_args()


def get_config():
    '''Returns an array with the relevant part of syncthing config:
    [
        { "folder_label": "label_of_first_folder",
          "path": "local/path/of/first/folder"
        },
        { "folder_label": "label_of_second_folder",
          "path": "local/path/of/second/folder"
        }
    ]
    '''
    filepath = os.path.expanduser("~/.config/syncthing/config.xml")

    result = []

    # Workaround to allow write access to variables from inner functions
    in_configuration = [False]
    depth_counter = [0]


    def cb_start_element(name, attrs):
        '''expat callback'''

        depth_counter[0] = depth_counter[0] + 1
        if name == "configuration":
            in_configuration[0] = True
        if in_configuration[0] and name == "folder" and depth_counter[0] == 2:
            result.append(
                {"folder_label" : attrs["label"], "path": attrs["path"]})

    def cb_end_element(name):
        '''expat callback'''

        depth_counter[0] = depth_counter[0] - 1
        if name == "configuration" and in_configuration[0]:
            in_configuration[0] = False



    with open(filepath, "r") as filehandle:
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = cb_start_element
        parser.EndElementHandler = cb_end_element
        parser.ParseFile(filehandle)
        return result


def find_conflict_files(folder_path):
    '''Returns an array of Syncthing conflict files for the given folder path'''
    result = []
    pattern = ".sync-conflict-"
    for root, dirs, files in os.walk(folder_path):
        for dir_ in dirs:
            if dir_.find(pattern) >= 0:
                result.append(os.path.join(root, dir_))
        for file_ in files:
            if file_.find(pattern) >= 0:
                result.append(os.path.join(root, file_))
    return result


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    config = get_config()

    if args.quiet:
        for entry in config:
            conflicts = find_conflict_files(entry["path"])
            for conflict in conflicts:
                print(conflict)
    else:
        first = True
        for entry in config:
            if not first:
                print("")
            print("Checking folder " + entry["folder_label"] + ":")
            conflicts = find_conflict_files(entry["path"])
            if not conflicts:
                print("No conflicts found")
            else:
                for conflict in conflicts:
                    print("  " + conflict)
            first = False

if __name__ == "__main__":
    main()
