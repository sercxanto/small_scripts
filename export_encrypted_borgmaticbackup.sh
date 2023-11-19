#!/usr/bin/env bash
#
# Exports an encrypted borgmatic backup to a tar.gpg file
#
# The MIT License (MIT)
#
# Copyright (c) 2023 Georg Lutz <georg@georglutz.de>
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

set -e

script_name=$(basename "$0")

function help()
{
    echo "Exports an encrypted borgmatic backup to a tar.gpg file"
    echo ""
    echo ""
    echo "Usage:"
    echo "$script_name [-r repository] config outfile"
    echo ""
    echo "  -r repository: Path of repository to export from, defaults to the configured"
    echo "                 repository if there is only one"    
    echo "  config: Path of borgmatic config file"
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

while getopts "hr:" OPTIONS; do
    case ${OPTIONS} in
        h) help; exit ;;
        r) BORGMATIC_REPO="${OPTARG}" ;;
        *) help; exit 1 ;;
    esac
done

shift $(($OPTIND - 1))

if [ $# -ne 2 ]; then
    help
    exit 1
fi

BORGMATIC_CONFIG="$1"
GPG_FILE="$2"

repo_cmdline=""
if [ ! -z "$BORGMATIC_REPO" ]; then
    repo_cmdline="--repository $BORGMATIC_REPO"
fi

echo "Running borgmatic export-tar ..."

set -x
borgmatic -c $BORGMATIC_CONFIG export-tar \
    $repo_cmdline --archive latest --destination - \
    | gpg --encrypt --sign --default-recipient-self -o "$GPG_FILE"

echo "Finished successfully"
