small_scripts
=============

Simple scripts to small for own repo

copy duplicity backups
======================

This script copies/duplicates local [duplicity](http://duplicity.nongnu.org/)
backup files.

You can specify the amount of past backups runs. By default the last two full
backups and their incrementals are copied, older files are automatically
deleted (sliding window of most recent backups).

Use this script to add another level of redunancy in case that the main backup
location fails.

The software, i.e. file naming conventions has been tested with duplicity
version 0.6.13 (yes I know, quite old).

In case of any error the scripts exits with a return code != 0.


Usage examples
--------------

Copy with standard arguments (last two full backups and associated
incrementals), older backups / other files at dst folder will be deleted:

    ./copy_duplicity_backups.py /mnt/src /mnt/dst

Show which files would would be deleted/copied without actually writing
anything to disk:

    ./copy_duplicity_backups.py --dryrun /mnt/src /mnt/dst

Copy last 5 backups and associated incrementals:

    ./copy_duplicity_backups.py --nr 5 /mnt/src /mnt/dst

Limit size of dst folder to 5GB. Backups are copied until limit is reached:

    ./copy_duplicity_backups.py --maxsize 5000 /mnt/src /mnt/dst

Do not output anything - only in case of errors:

    ./copy_duplicity_backups.py --quiet /mnt/src /mnt/dst

