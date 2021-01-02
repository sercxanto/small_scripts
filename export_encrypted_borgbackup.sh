#!/bin/bash
#
# Exports an encrypted borg backup to a tar.gpg file
#
# The MIT License (MIT)
#
# Copyright (c) 2019-present Georg Lutz <georg@georglutz.de>
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
    echo "Exports an encrypted borg backup to a tar.gpg file"
    echo ""
    echo ""
    echo "Usage:"
    echo "$script_name archive outfile"
    echo ""
    echo "  archive: The borg archive to export."
    echo "  outfile: Where to place the resulting tar.gpg file."
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

opt_archive="$1"
opt_outfile="$2"


set +e
echo "Checking archive $opt_archive ..."
borg info $opt_archive
rc=$?

if [ $rc -ne 0 ]; then
    echo "borg info did not return 0. Exit"
    exit 1
fi

echo "Running borg export-tar ..."

borg export-tar --progress $opt_archive -  | gpg --encrypt --sign --default-recipient-self -o "$opt_outfile"

echo "Finished successfully"
