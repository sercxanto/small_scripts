#!/usr/bin/env bash
#
# Installs scripts in ~/bin

set -eu
SCRIPT_DIR=$(readlink -f $(dirname $0))

source $SCRIPT_DIR/config

for file in $FILES_TO_LINK; do
    file_in_bin=~/bin/$file
    dest_should=$SCRIPT_DIR/$file
    # readlink -e reports empty string for non existing files
    if [ -L $file_in_bin ]; then
        dest_is=$(readlink -f $file_in_bin)
    else
        dest_is=
    fi
    if [ "$dest_is" != "$dest_should" ]; then
        echo link  $file_in_bin -\> $dest_should
        ln -sf   $dest_should $file_in_bin
    fi
done

if command -v go > /dev/null; then
    echo "Building go files"
    cd $SCRIPT_DIR/barclaycard2homebank
    go build -o ~/bin
    cd $SCRIPT_DIR/moneywallet2homebank
    go build -o ~/bin    
else
    echo "Go not found. Skipping go files."
fi