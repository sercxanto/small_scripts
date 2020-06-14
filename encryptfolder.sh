#!/bin/bash
#
# Encrypts and signs a folder to a tar.gpg file
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Georg Lutz <georg@georglutz.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

set -eu

script_name=$(basename "$0")

function help()
{
    echo "Encrypts and signs a folder to a tar.gpg file."
    echo ""
    echo ""
    echo "Usage:"
    echo "$script_name infolder outfolder"
    echo ""
    echo "  folder: Folder recursively "
    echo "  outfolder: Where to place the resulting tar.gpg file. Basename is the name of infolder."
    echo ""
}

function error()
{
    local lineno="$1"
    echo "Error in line $lineno"
    exit 1
}

trap 'error ${LINENO}' ERR


if [ $# -ne 2 ]; then
    help
    exit 1
fi

opt_infolder="$1"
opt_outfolder="$2"

if [ ! -d "$opt_infolder" ]; then
    echo "Folder $opt_infolder not found. Exit."
    exit 1
fi


if [ ! -d "$opt_outfolder" ]; then
    echo "Folder $opt_outfolder not found. Exit."
    exit 1
fi

outfile="$opt_outfolder"/$(basename "$opt_infolder").tar.gpg

if [ -x "$outfile" ]; then
    echo "$outfile already exists. Exit."
fi

echo "Writing to $outfile"

tar -cf - "$opt_infolder" | gpg --encrypt --sign --default-recipient-self -o "$outfile"
