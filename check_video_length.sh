#!/bin/bash
#
# Checks video files in a folder to have a minimal length.
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Georg Lutz <georg@georglutz.de>
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

script_name=$(basename $0)

function help()
{
    echo "Checks video files in a folder to have a minimal length."
    echo "Can be used e.g. to detect ripping errors."
    echo ""
    echo "Uses mplayer."
    echo ""
    echo "$script_name folder minimal_length"
    echo ""
    echo "  folder: Folder recursively scanned"
    echo "  minimal_lenth: Minimal length of video file in seconds"
    echo ""
    echo "Example output:"
    echo ""
    echo "$ $script_name . 40"
    echo "  NOK file1.mpeg 30"
    echo "  OK  file2.mpeg 40"
}


function error()
{
    local lineno="$1"
    echo "Error in line $lineno"
    exit 1
}

trap 'error ${LINENO}' ERR


# Returns length in seconds of given movie file on stdout
# 
# Returns "0" in case of error
#
# Usage: get_length movie file
function get_length()
{
    local filename="$1"
    local result=0
    if [ ! -f $filename ]; then
        echo 0
        return;
    fi
    local tmpfile=$(mktemp --tmpdir ${script_name}_XXXXX)
    set +e
    mplayer -identify -frames 0 -vc null -vo null -ao null "$filename" 1>$tmpfile 2>/dev/null
    rc=$?
    if [ $rc -ne 0 ]; then
        rm $tmpfile
        echo 0
        return
    fi
    local tmpfile2=$(mktemp --tmpdir ${script_name}_XXXXX)
    grep "^ID_LENGTH=" $tmpfile | sed -e 's/ID_LENGTH=//' > $tmpfile2
    # grep returns 0 if found, > 0 if not found or error
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        rm $tmpfile
        rm $tmpfile2
        echo 0
        return
    fi
    set -e
    # cut decimal fraction part
    echo $(cat $tmpfile2) / 1 | bc
    rm $tmpfile
    rm $tmpfile2
}


if [ $# -ne 2 ]; then
    help
    exit 1
fi

opt_folder="$1"
opt_minimal_length=$2
if [ ! -d "$opt_folder" ]; then
    echo "Folder not found. Exit."
    exit 1
fi
if ! [[ $opt_minimal_length =~ ^[0-9]+$ ]]; then
    help
    exit 1
fi

while IFS= read -d $'\0' -r file ; do
    length=$(get_length "$file")
    result_line=
    if (( $length < $opt_minimal_length )); then
        result_line="NOK"
    else
        result_line="OK "
    fi
    result_line="$result_line $file $length"
    echo $result_line
done < <(find "$opt_folder" -type f -print0)


