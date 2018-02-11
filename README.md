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


gnucash_import
==============

Yet another gnucash import script.

Parses a CSV file and directly imports it into gnucash. Example usage:

    gnucash_import.py csv_file myfile.gnucash "Aktiva:Barvermögen:Girokonto"

The CSV file is expected to be in an defined format, containing already information on the account of the cross entry (double-accounting) and a description for the booking:

    date;accountname;description;value
    2017-01-01;abcd:efg;Some description;2.31
    2017-01-02;xyz:abc;Some other description;1.23

With the plain CSV import builtin into Gnucash the user has to confirm the account mapping based on the description.

The license is GPLv2 because of linking to Gnucashs python libraries.


gnucash_accounts
================

Returns list of accounts defined in a gnucash file.

Example:

    $ ./gnucash_accounts.py gnucash.gnucash 
    Aktiva:Barvermögen:Bargeld
    Aktiva:Barvermögen:Girokonto
    Aktiva:Barvermögen:Sparkonto
    [...]

The license is GPLv2 because of linking to Gnucashs python libraries.


msmtpq_notify.py
================

msmtpq_notify - Notifies desktop user if msmtpq has actually sent or enqueued mail

When using msmtpq in front of msmtp all failed connection attempts to the
mailserver results in the mail being silently added to the queue.

While this is a desired behaviour in most cases it may be fatal when msmtp or
the mail server is misconfigured. In this case msmtp may always fails and mail
never becomes delivered.

This script is a wrapper script which can be run itself in front of msmtQ.
After the call to msmtpQ it informs the user about the number of entries in the
queue. It does so by checking the queue before and after the call to "msmtpQ"
with "msmtpq -d".

So the user has the chance to be informed if something still hangs in the queue
an can manually intervent. Alternatively the latest versions of msmtpq also
run/flush the queue on the next call to msmtpQ.

msmtpq_notify.py uses the the deskop notification daemon which is available in
most modern Linux desktop environments. To be able to communicate with the
daeamon you need to install notify-send before. In Ubuntu it is available in
the package libnotify-bin.

msmtpq_notify.py passes stdin and all arguments over to msmtpq and returns its
exit code back (although the last version seems to always return with 0, even
if msmtp reported some error). For debugging purposes create a symlink
msmtpq_notify_debug.py. If called as msmtpq_notify_debug.py it will output
additional traces.



symlink\_picture\_list
======================

Creates an ordered symlinked folder structure to pictures out of a list in a file.

The script expects two arguments: indir and outdir.

indir is a folder structure like the following:

```
indir/
├── 2015
│   └── 2015_mybest_pics
│       ├── filelist.txt
│       └── index.md
├── 2017-07_berlin_trip
│   ├── filelist.txt
│   └── index.md
├── 2017-07_frankfurt_trip
│   ├── filelist.txt
│   └── index.md
...
```

The filelist.txt files contain pathes where the actual pictures are stored, each name in a new line, e.g. for `2015_mybest_pics`:

    /home/user/pics/2015/01/11/pic0001.jpg
    /home/user/pics/2015/03/11/pic0087.jpg
 

This would result in the following outdir:

```
outdir
├── 2015
│   └── 2015_mybest_pics
│       ├── 000_pic0001.jpg -> /home/user/pics/2015/01/11/pic0001.jpg
│       ├── 001_pic0002.jpg -> /home/user/pics/2015/03/11/pic0087.jpg
│       ├── index.md -> /path/to/indir/2015/2015_mybest_pics/index.md
...
```

Any other file that is not named `filelist.txt` will be symlinked to outdir as well.

outdir can be fed into any static gallery generator like [sigal](http://sigal.saimon.org) which parses folders recursively. The benefit is that you don't have to store a copy of all files on your harddisk and that you can define an order in which the pictures should appear in the gallery.
