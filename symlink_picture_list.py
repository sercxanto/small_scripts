#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" symlink_picture_list.py

    Creates symlinks to pictures out of a list in a file"""

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
import logging
import os
import sys


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Creates symlinks to pictures out of a list in a file")
    parser.add_argument(
        "-v", "--verbose", dest="debuglevel", action="store_const",
        const=logging.DEBUG, default=logging.INFO,
        help="Enables verbose/debug output.")
    parser.add_argument(
        "indir",
        help="directory structure with filelist.txt files, one path name per line")
    parser.add_argument(
        "outdir",
        help="folder name for writing the symlinks")
    return parser.parse_args()


def read_list(filepath):
    '''Reads the list from filepath and returns an array with filenames'''
    result = []
    file_ = open(filepath, "r")
    for line in file_:
        if len(line) <= 1 or line.startswith("#"): # Skip empty and comment lines
            pass
        else:
            result.append(line.strip())
    return result


def check_and_create_symlink(source, symlink_file):
    '''Checks and creates a symlink if possible

    Arguments:
       source: where the symlink points to
       symlink_file: the filesystem entry representing the symlink

    Calls sys.exit(1) in case that a symlink exists, but points to another source.
       '''
    if os.path.lexists(symlink_file):
        if os.path.islink(symlink_file) and os.readlink(symlink_file) == source:
            logging.debug("Symlink " + symlink_file + " to " + source + "already exists. Skip")
        else:
            logging.error("%s exists, but does not point to %s", symlink_file, source)
            sys.exit(1)
    else:
        logging.info("Symlink " + source + " to " + symlink_file)
        os.symlink(source, symlink_file)


def symlink_files(filelist, outdir):
    '''Symlinks the files in list to outdir.

    All filenames are pretended by 000_, 001_, 002_ etc.'''

    counter = 0

    for entry in filelist:
        old_filename = os.path.basename(entry)
        new_filename = "%03d_%s" % (counter, old_filename)
        new_pathname = os.path.join(outdir, new_filename)
        check_and_create_symlink(entry, new_pathname)
        counter = counter + 1


def get_dest_path(root, dir_entry, indir, outdir):
    '''Helper function for generate_folder_structure, returns file/folder path in outdir'''
    full_path = os.path.join(root, dir_entry)
    rel_path = os.path.relpath(full_path, indir)
    dest_path = os.path.join(outdir, rel_path)
    return dest_path


def generate_folder_structure(indir, outdir):
    '''Iterates over folder structure in indir and generates folder structure in outdir

    * any subfolder in indir will be also created in outdir
    * filelist.txt files are parsed and the containing file names are symlinked
    * any other file will be symlinked to indir
    '''
    for root, dirs, files in os.walk(indir):
        for file_ in files:
            full_path = os.path.join(root, file_)
            if file_ == "filelist.txt":
                # Read content of filelist.txt and create symlinks for all the files
                logging.debug("found filelist at " + full_path)
                filelist = read_list(full_path)
                symlink_files(filelist, get_dest_path(root, "", indir, outdir))
            else:
                # Symlink single file
                logging.debug("found other file " + full_path)
                dest_path = get_dest_path(root, file_, indir, outdir)
                check_and_create_symlink(os.path.abspath(full_path), dest_path)
        for dir_ in dirs:
            full_path = os.path.join(root, dir_)
            logging.debug("found dir " + full_path)
            dest_path = get_dest_path(root, dir_, indir, outdir)
            if not os.path.exists(dest_path):
                logging.info(" Create dir " + dest_path)
                os.mkdir(dest_path)
            else:
                logging.debug(" Dir %s already exists. Skip", dest_path)


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    logging.basicConfig(format="%(message)s", level=args.debuglevel)
    if not os.path.isdir(args.indir):
        logging.error("Given argument is not a directory: %s. Exit.", args.indir)
        sys.exit(1)
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)


    generate_folder_structure(args.indir, args.outdir)

if __name__ == "__main__":
    main()
