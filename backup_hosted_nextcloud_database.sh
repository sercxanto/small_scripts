#!/usr/bin/env bash
#
# Backs up nextcloud calendar and addressbooks
#
# The MIT License (MIT)
#
# Copyright (c) 2022 Georg Lutz <georg@georglutz.de>
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
default_settings_file="$HOME/.$(basename "$script_name" .sh)"

function help()
{
    echo "Backs up nextcloud calendars and addressbooks"
    echo ""
    echo ""
    echo "Usage:"
    echo "$script_name [settings-file]"
    echo ""
    echo "  settings-file: A file with settings (default: $default_settings_file)"
    echo ""
    echo ""
    echo "Format of settings file:"
    echo "========================"
    echo ""
    cat << SETTINGS_EXAMPLE
# When served under "https://nextcloud.example.com" enter "nextcloud.example.com" here
# Only sub-domain is supported not sub-folder
NEXTCLOUD_SERVER=nextcloud.example.com

# The username to login to the nextcloud instance
USERNAME=my_username

# The password to login to the nextcloud instance
# Hint: Use a scripting compatible password manager like pass
PASSWORD=\$(pass nextcloud.example.com)

# The local base directory where to store the calendars and contacts
#
# The following files will be created there:
# <calendar-name>.ics
# <contacts-name>.vcf
OUT_DIR=~/mirror/nextcloud.example.com

# A space separated list of calendar names
CALENDARS="acalendar bcalendar"

# A space separated list of addressbooks
ADDRESSBOOKS="contacts"
SETTINGS_EXAMPLE
    echo ""
}

if [ $# = 1 ]; then
    if [ "$1" = "-h" ]; then
        help
        exit 0
    else
        settings_file="$1"
    fi
else
    settings_file="$default_settings_file"
fi

if [ ! -e "$settings_file" ]; then
    echo "Settings file '$settings_file' cannot be found"
    exit 1
fi

# shellcheck source=/dev/null
. "$settings_file"

expected_vars="NEXTCLOUD_SERVER USERNAME PASSWORD OUT_DIR CALENDARS ADDRESSBOOKS"

for var in $expected_vars; do
    if [[ ! -v $var ]]; then
        echo "Setup incorrect. The following variables must be set:"
        echo "$expected_vars"
        exit 1
    fi
done

nextcloud_url="https://$NEXTCLOUD_SERVER"

for calendar in $CALENDARS; do
    echo "Downloading calender '$calendar' ..."
    curl -s -S --fail --netrc-file <(cat <<<"machine $NEXTCLOUD_SERVER login $USERNAME password $PASSWORD") \
        "$nextcloud_url"/remote.php/dav/calendars/"$USERNAME"/"$calendar"?export \
        -o "$OUT_DIR"/"$calendar".ics
done

for addressbook in $ADDRESSBOOKS; do
    echo "Downloading addressbook '$addressbook' ..."
    curl -s -S --fail --netrc-file <(cat <<<"machine $NEXTCLOUD_SERVER login $USERNAME password $PASSWORD") \
        "$nextcloud_url"/remote.php/dav/addressbooks/users/"$USERNAME"/"$addressbook"/?export \
        -o "$OUT_DIR"/"$addressbook".vcf
done

echo "Download finished successfully"