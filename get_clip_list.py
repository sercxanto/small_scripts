#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" get_clip_list.py
    Generates a CSV list of video files"""

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
import distutils.spawn
import json
import logging
import os
import subprocess
import sys


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Generates a CSV list of video files. Based on ffprobe/ffmpeg.")
    parser.add_argument(
        "folder",
        help="Folder name of video clips.")
    parser.add_argument(
        "csvfile",
        help="File name of the CSV file, will be overwritten if existent.")

    return parser.parse_args()


def get_file_list(folder):
    '''Returns a sorted filelist of the given folder'''

    result = []
    for (dirpath, _, filenames) in os.walk(folder):
        result.extend(
            [os.path.join(dirpath, filename) for filename in filenames])
    return result


def get_json_info_ffprobe(filename):
    '''Returns json info on filename for first video stream'''
    args = [
        "ffprobe", "-show_streams", "-print_format", "json", "-v", "quiet",
        "-select_streams", "video", filename
        ]
    logging.info("Running ffprobe on %s", filename)
    proc = subprocess.Popen(args=args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    (stdout_data, stderr_data) = proc.communicate(timeout=15)

    if proc.returncode != 0:
        logging.warning("ffmpeg returned non zero exit code for %s:", filename)
        for line in stderr_data:
            logging.warning("  %s", line)
        for line in stdout_data:
            logging.warning("  %s", line)
        return None

    return stdout_data


def get_clips_info(folder, filelist):
    '''Returns information on a list of files

    Parameters:

    filelist: List of files as ommited by get_file_list
    folder: Base folder of files

    Returns:

    [
       {
           filename: "abc",
           size_mb: 1.2,
           duration_s: 60,
           timestamp: "2019-01-01 13:14:01"
       },
       {
           filename: "abcd",
           size_mb: 2.1,
           duration_s: 30,
           timestamp: "2019-01-01 13:15:01"
       }
    ]
    '''

    result = []

    for file_ in filelist:
        info = {}
        info["filename"] = os.path.relpath(file_, folder)
        info["size_mb"] = os.path.getsize(file_) / 1000000
        json_info = get_json_info_ffprobe(file_)
        if json_info != None:
            json_decoded = json.loads(json_info.decode())
            info["duration_s"] = json_decoded["streams"][0]["duration"]
            try:
                # creation_time is something like "2019-04-16T19:33:33.000000Z"
                timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                info["timestamp"] = datetime.datetime.strptime(
                    json_decoded["streams"][0]['tags']['creation_time'],
                    timestamp_format)
            except KeyError:
                logging.warning("Cannot parse creation_time")
        result.append(info)
    return result


def convert_clips_info_to_csv(clips_infos, csvfile):
    '''Convert clips_infos as returned by get_clips_info to csvfile'''

    with open(csvfile, 'w', newline='') as file_:
        fieldnames = ["filename", "size_mb", "duration_s", "timestamp"]
        writer = csv.DictWriter(file_, fieldnames=fieldnames, restval="N/A", delimiter=";")
        writer.writeheader()
        for clip_info in clips_infos:
            writer.writerow(clip_info)


def main():
    '''main function, called when script file is executed directly'''

    logging.basicConfig(format="%(message)s", level=logging.INFO)
    args = get_args()

    if not distutils.spawn.find_executable("ffprobe"):
        logging.error("Cannot find ffprobe. Install ffmpeg first")
        sys.exit(1)

    file_list = get_file_list(args.folder)
    file_list.sort()

    clips_info = get_clips_info(args.folder, file_list)

    convert_clips_info_to_csv(clips_info, args.csvfile)


if __name__ == "__main__":
    main()
