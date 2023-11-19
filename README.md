# small_scripts

Simple scripts to small for own repo:

* `backup_hosted_nextcloud_database.sh`: Backs up nextcloud calendar and addressbooks
* `barclaycard2homebank`: Convert barclaycard visa excel transaction report to homebank CSV format
* `check_video_length.sh`: Checks video files in a folder to have a minimal length
* `copy_duplicity_backups.py`: Copies most recent duplicity backup files
* `encryptfolder.sh`: Encrypts and signs a folder to a tar.gpg file
* `export_encrypted_borgbackup.sh`: Exports an encrypted borg backup to a tar.gpg file
* `export_encrypted_borgmaticbackup.sh`: Exports an encrypted borgmatic backup to a tar.gpg file
* `fiducia2homebank.py`: Convert the CSV export of fiducia driven banking websites,
    i.e. Volksbank to homebank csv format
* `find_orphaned_sidecar_files.py`: Find sidecar files (like XMP) which don't have the associated base file anymore
* `fix_comdirect_csv.py`: Fix the CSV export of comdirect bank
* `fix_fiducia_csv.py`: Fix the CSV export of fiducia driven banking websites
* `get_clip_list.py`: Generates a CSV list of video files
* `gnucash_accounts.py`: Get list of accounts from gnucash
* `gnucash_import.py`: Yet another import script for gnucash
* `maildir_trash.sh`: Purge mails older than 30 days from Maildir trash folder
* `moneywallet2homebank`: Convert moneywallet CSV to homebank CSV format
* `msmtpq_notify.py`: Notifies desktop user if msmtpq has actually sent or enqueued mail
* `mutt_flagged_vfolder_jump.py`: Generates mutt command file to jump to the source of a symlinked mail
* `mutt_flagged_vfolder_link.py`: Searches flagged mails and symlinks them to a (vfolder) maildir
* `paypal2homebank.py`: Convert the CSV export of paypal to homebank CSV format
* `sendmail_wrapper.py`: `/usr/sbin/sendmail` replacement for systems without an own local mail server
* `smtpcheckaddresses.py`: Checks list of mail addresses at mail server
* `start_firefox_cleanprofile.py`: Starts firefox with an empty (clean) profile
* `start_ssh_agent.sh`: Starts SSH agent and sets environment variable
* `symlink_picture_list.sh`: Creates symlinks to pictures out of a list in a file
* `syncthing_findconflicts.py`: Scans all folders of the local Syncthing instance for conflict files
* `syncthing_rescan.py`: Manually triggers a rescan of the local Syncthing instance

## backup_hosted_nextcloud_database.sh

In a hosted environment you ususally don't have direct access to the database
where calendars and contacts are stored.

And even when the provider has some sort of backup

* you don't really own it, because you can't download it
    * e.g. you don't can't just migrate in case you are locked out for some reason
* its an "all or nothing" story when it comes to restores
    * the whole instance/account is reset to some point in time
    * any change in between the last backup is effectively overwritten

Enter backup_hosted_nextcloud_database.sh:

Create a settings file `~/.backup_hosted_nextcloud_database.sh`
(a commented example can be in the script help page with "-h"):

```shell
NEXTCLOUD_SERVER=nextcloud.example.com
USERNAME=my_username
PASSWORD=$(pass nextcloud.example.com)
OUT_DIR=~/mirror/nextcloud.example.com
CALENDARS="acalendar bcalendar"
ADDRESSBOOKS="contacts"
```

Run the scripts and ICS and VCF files are written to `~/mirror/nextcloud.example.com`:

```shell
$ backup_hosted_nextcloud_database.sh
Downloading calender 'acalendar' ...
Downloading calender 'bcalendar' ...
Downloading addressbook 'contacts' ...
Download finished successfully
```

## barclaycard2homebank

barclaycard2homebank is a tool which converts excel transaction exports from barclaycard to the CSV homebank format:

```shell
$ barclaycard2homebank Umsaetze.xlsx out.csv
barclaycard2homebank.go:100: infile Umsaetze.xlsx
barclaycard2homebank.go:101: outfile out.csv
barclaycard2homebank.go:153: Header found in line 12
barclaycard2homebank.go:144: Processing line 13
barclaycard2homebank.go:144: Processing line 14
barclaycard2homebank.go:144: Processing line 15
barclaycard2homebank.go:144: Processing line 16
barclaycard2homebank.go:144: Processing line 17
barclaycard2homebank.go:144: Processing line 18
barclaycard2homebank.go:165: Writing to file out.csv
```

## check_video_length

Imagine to batch processs video DVDs with [handbrake](https://handbrake.fr/) to make a backup copy or transcode it to some other format. In some cases the DVD might have errors and produce a truncated version of video files only.

You want to make sure that at least the produced output are valid videofiles and that the have a minimal number of seconds in it.

`check_video_length.sh` reads out the metadata of video files with the help of mplayer and makes sure that they have a minimum number of playtime in seconds at least.

Example:

```shell
$ check_video_length.sh /some/folder 60
NOK /some/folder/20190413_194624.MP4 20
OK /some/folder/20190413_194624.MP4 70
```

## copy duplicity backups

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

### Usage examples

Copy with standard arguments (last two full backups and associated
incrementals), older backups / other files at dst folder will be deleted:

```shell
./copy_duplicity_backups.py /mnt/src /mnt/dst
```

Show which files would would be deleted/copied without actually writing
anything to disk:

```shell
./copy_duplicity_backups.py --dryrun /mnt/src /mnt/dst
```

Copy last 5 backups and associated incrementals:

```shell
./copy_duplicity_backups.py --nr 5 /mnt/src /mnt/dst
```

Limit size of dst folder to 5GB. Backups are copied until limit is reached:

```shell
./copy_duplicity_backups.py --maxsize 5000 /mnt/src /mnt/dst
```

Do not output anything - only in case of errors:

```shell
./copy_duplicity_backups.py --quiet /mnt/src /mnt/dst
```

## encryptfolder.sh

This simple shell script archives a folder to a tar.gpg file.

Example:

```shell
$ encryptfolder.sh small_scripts /tmp
Writing to /tmp/small_scripts.tar.gpg
```

Depending on your local setup a popup appears to enter the password for your private key.

The resulting file is encrypted and signed with the default GPG identity:

```shell
$ gpg -d /tmp/small_scripts.tar.gpg | tar -t
small_scripts/
small_scripts/install.sh
small_scripts/.gitignore
small_scripts/mutt_flagged_vfolder_jump.py
small_scripts/copy_duplicity_backups.py
[...]
```

## export_encrypted_borgbackup

[Borgbackup](https://www.borgbackup.org/) is a deduplicating backup program with encryption and compresssion. It uses a sophisticated [storage format](https://borgbackup.readthedocs.io/en/stable/internals/data-structures.html) to fullfill those features.

Each backup run is stored in a so called [archive](https://borgbackup.readthedocs.io/en/stable/quickstart.html#archives-and-repositories). Sometimes you may want to keep a specific archive in long term storage - indepenend of any specific software specific format - let say as regular tar file.

`export_encrypted_borgbackup.sh` is a simple wrapper around borgbackup's export-tar command encrypts and sign with gnupgs main identify keys.

Usage example (assuming that the env variable BORG_REPO is set):

```shell
$ export_encrypted_borgbackup.sh ::hostname-2020-06-05_22:19:17 /tmp/out.tar.gpg
[...]
$ file /tmp/out.tar.gpg
/tmp/out.tar.gpg: PGP RSA encrypted session key - keyid: xxxx RSA (Encrypt or Sign) 4096b .
```

## export_encrypted_borgmaticbackup

Like `export_encrypted_borgbackup`, but with borgmatic:

```shell
$ export_encrypted_borgmaticbackup.sh -r /path/to/repo my_borgmatic.yaml /tmp/out.tar.gpg
[...]
$ file /tmp/out.tar.gpg
/tmp/out.tar.gpg: PGP RSA encrypted session key - keyid: xxxx RSA (Encrypt or Sign) 4096b .
```

It exports the last archive of the mentioned config / repo.

## fiducia2homebank

`fiducia2homebank.py` converts the CSV export of fiducia based banking websites (e.g. Volksbank ) to the [CSV import format](http://homebank.free.fr/help/misc-csvformat.html) of [homebank](http://homebank.free.fr).

Example:

```shell
$ fiducia2homebank.py Umsaetze_DExxxxxxxxxxxxxx_2020.01.01.csv ~/out.csv
Found header in line 9
Data section ends in line 42
```

## find_orphaned_sidecar_files.py

Some software like digital image processing tools work with [sidecar](https://en.wikipedia.org/wiki/Sidecar_file) files which are placed next to the original file. E.g. [darktable](https://www.darktable.org/) uses `.xmp` as file extension, [rawtherapee](https://www.rawtherapee.com/) `.pp3`.

When you sort out / delete original files outside of the software, you end up with orphaned sidecar files.

`find_orphaned_sidecar_files.py` helps in such a situation by finds such duplicates.

Example usage:

```shell
$ find_orphaned_sidecar_files.py pics
pics/dir1/orphaned1.xmp
pics/dir2/orphaned2.xmp
```

## get_clip_list

`get_clip_list.py` scans a folder of video clips, reads out the meta data like filename, size in MB, duration in seconds and the timestamp and stores it in a csv file.

You can use it, e.g. for input in a spread sheet for statistics or to prepare for rearranging clips in video editing software.

Example:

```shell
$ get_clip_list_py somefolder out.csv
$ cat out.csv
filename;size_mb;duration_s;timestamp
2019_0412_155905_086.MP4;88.858065;24.920000;2019-04-12 15:59:29
2019_0412_160114_087.MP4;73.516233;20.620000;2019-04-12 16:01:34
2019_0412_161258_088.MP4;131.910425;37.020000;2019-04-12 16:13:34
```

## gnucash_import

Yet another gnucash import script.

Parses a CSV file and directly imports it into gnucash. Example usage:

```shell
gnucash_import.py csv_file myfile.gnucash "Aktiva:Barvermögen:Girokonto"
```

The CSV file is expected to be in an defined format, containing already information on the account of the cross entry (double-accounting) and a description for the booking:

```csv
date;accountname;description;value
2017-01-01;abcd:efg;Some description;2.31
2017-01-02;xyz:abc;Some other description;1.23
```

With the plain CSV import builtin into Gnucash the user has to confirm the account mapping based on the description.

The license is GPLv2 because of linking to Gnucashs python libraries.

## gnucash_accounts

Returns list of accounts defined in a gnucash file.

Example:

```shell
$ ./gnucash_accounts.py gnucash.gnucash 
Aktiva:Barvermögen:Bargeld
Aktiva:Barvermögen:Girokonto
Aktiva:Barvermögen:Sparkonto
[...]
```

The license is GPLv2 because of linking to Gnucashs python libraries.

## moneywallt2homebank

moneywallt2homebank is a tool which converts CSV export of moneywallt to the CSV homebank format:

```shell
$ moneywallet2homebank MoneyWallet_export_1.csv out.csv
moneywallet2homebank.go:120: infile MoneyWallet_export_1.csv
moneywallet2homebank.go:121: outfile out.csv
moneywallet2homebank.go:152: Processing line 1
moneywallet2homebank.go:152: Processing line 2
moneywallet2homebank.go:152: Processing line 3
moneywallet2homebank.go:152: Processing line 4
moneywallet2homebank.go:152: Processing line 5
moneywallet2homebank.go:152: Processing line 6
moneywallet2homebank.go:168: Writing to file out.csv
```

## msmtpq_notify.py

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

## mutt_flagged_vfolder

`mutt_flagged_vfolder_link.py` and `mutt_flagged_vfolder_jump.py` can be used to create a "virtual maildir folder" with flagged mails:

A virtual maildir folder is a folder with symlinks pointing to the original flagged mail.

### `mutt_flagged_vfolder_link.py MAILDIR VFOLDER`

When called in the folder MAILDIR, creates a symlinked file in VFOLDER for every flagged mail.

Add it to your muttrc the following way:

```text
folder-hook . 'macro index F "<flag-message><enter-command>unset wait_key^m<sync-mailbox><shell-escape>mutt_flagged_vfolder_link.py ~/Maildir ~/Maildir/.flagged^m<enter-command>set wait_key^m"'
```

### `mutt_flagged_vfolder_jump.py VFOLDER CMDFILE`, the message is on stdin

When called in a virtual folder with symlinked mails, jumps to the original message location provided by mutt on stdin. It deletes all previous flagged emails.

Add it to your muttrc the following way:

```text
folder-hook ".*flagged*" 'macro index F "<enter-command>unset wait_key^m<pipe-entry>mutt_flagged_vfolder_jump.py ~/Maildir/.flagged ~/tmp/mutt_flagged_vfolder_jump<enter><enter-command>source ~/tmp/mutt_flagged_vfolder_jump^m<enter-command>set wait_key^m"'
```

For the full story, read [mutt_flagged_vfolder_README.md](mutt_flagged_vfolder_README.md).

## offlineimap_refresh

[offlineimap](http://www.offlineimap.org/) is a python based tool to synchronize a remote IMAP mailbox to a local Maildir folder structure. Usually it is started in background and starts the synchronization in regular intervals (`autorefresh` setting). If the offlineimap receives a SIGUSR signal it manually triggers the synchronisation as soon as possible. This is exactly what `offlineimap_refresh.sh` is doing.

## paypal2homebank

`paypal2homebank.py` converts the CSV export of paypal to the [CSV import format](http://homebank.free.fr/help/misc-csvformat.html) of [homebank](http://homebank.free.fr).

Example:

```shell
$ paypal2homebank.py ~/bin/Download.CSV ~/out.csv
Processing line 1
Processing line 2
Skipping type Memo in line 3
```

`Download.CSV` is the file you get when you go to ["Download activities"](https://business.paypal.com/merchantdata/reportHome?reportType=DLOG) in the WebUI and choose "CSV" as format.

## sendmail_wrapper

`sendmail_wrapper.py` is a script which can be installed in server systems without an own local mail server.

It acts as a replacement for `/usr/sbin/sendmail` and forwards all local system emails (e.g. generated by cron) to a predefined external mail account.

It is compatible to the sendmail binary, but ignores all command line arguments like the recipient address.

The same setup could be accomplished basically also with other tools like with msmtp. But third party mail providers tend to block more and more system generated mails because of spam counter measures. One example is a mail header "From: root" or "To: root" which does not match the provider account address in the envelope headers. `sendmail_wrapper` patches these headers so that they conform to the configured third party mail provider and can be delivered.

### Configuration

The default config file is `/etc/sendmail_wrapper.ini`. The location can be overwritten by setting the environment variable `SENDMAIL_WRAPPER_CONFIG_FILE`.

The INI style config file is expected to have entries like in the following example:

```ini
from_address = <mailfrom@example.com>
to_address = <mailto@example.com>
servername = mail.example.com
port = 587
username = username
password = password
logfolder = /var/log/sendmail_wrapper
```

#### from_address / to_address

This is a RFC5322 compatible email address, including the enclosing "<>". Its is set as envelope and header address as some providers check that they are the same.

#### servername

This is the hostname for the SMTP server.

### port

This is the TCP port to connect to. The default mail submission agent port for clients is 587.

### username/password

The credentials to login into the SMTP server.

### logfolder

Optional, if set to a non empty value this points to a folder where logfiles will be written for every invocation.

The logfolder must exist and must be writeable by the user sendmail_wrapper is running under.

Caveat: Use for debugging only, sensitive information could be leaked, use with caution.

## smtpcheckaddresses

Checks given email addresses on SMTP level.

The intended use is to validate a MX email server configuration when it comes
to email addresses / domains. E.g. during a migration just before going in
production one might to check that all configured email address are accepted
and not bouncing.

smtpcheckaddresses.py accpepts a list of email addresses in a text file, one
line per address. For each address it then opens a connection to a given host
and checks the return code for the "RCPT TO" command. If the return code is in
the range 200 to 299 the email address is assumed to be "OK".

Additionally when given the -s option it sends a short test email to the
addresses so you can check that mails are really delivered locally and not
relayed. It is wise to provide also some email addresses which must fail.

## start_firefox_cleanprofile

There are numerous plugins for Firefox, some of them are very useful as they provide anti-tracking, security and privacy related features.

Nevertheless there are some websites having problems with these plugins. Private browsing mode is not an option in this case as by default most of the plugins are activated there too. If you just need to get things done quickly usually its the best to start with an empty profile in this case.

`start_firefox_cleanprofile.py` does exactly this: It starts firefox with an empty profile. All you have to to is to create a profile with the name "clean" before the first use:

```shell
    $ firefox -ProfileManager
    [Create a new profile with name "clean"]
    $ start_firefox_cleanprofile.py
    profile folder: /home/user/.mozilla/firefox/xxxxxxxx.clean
```

On every start the script wipes out the profile folder, deleting any traces of a previous session.

## start-ssh-agent

TODO: Describe

## symlink\_picture\_list

Creates an ordered symlinked folder structure to pictures out of a list in a file.

The script expects two arguments: indir and outdir.

indir is a folder structure like the following:

```text
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

```text
/home/user/pics/2015/01/11/pic0001.jpg
/home/user/pics/2015/03/11/pic0087.jpg
```

This would result in the following outdir:

```text
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

## syncthing_findconflicts

[Synthing](https://syncthing.net/) is an encrypted open source file synchronization tool. It synchronizes pairs of folders between two or more computers.

In case of a [conflict](https://docs.syncthing.net/users/faq.html#what-if-there-is-a-conflict) (a file changed on both sides since the last synchronization) the conflicting file is saved as `<filename>.sync-conflict-<date>-<time>-<modifiedBy>.<ext>`.

Depending on the change frequency this may happen from time to time. `syncthing_findconflicts.py` is a script which reads out the local Syncthing configuration reports sync conflict files found in those folders.

Example:

```shell
$ syncthing_findconflicts.py
Checking folder syncfolder1:
No conflicts found

Checking folder syncfolder2:
No conflicts found
```

## syncthing_rescan

[Synthing](https://syncthing.net/) is an encrypted open source file synchronization tool. It synchronizes pairs of folders between two or more computers.

The synchronization runs usually time triggered. From time to time there might be a need to start the synchronization manually.

`syncthing_rescan.py` reads out the local configuration and explicitely triggers a [rescan](https://docs.syncthing.net/rest/db-scan-post.html).

Example:

```shell
$ syncthing_rescan.py
Calling http://127.0.0.1:8384/rest/db/scan:
200 OK
b''
```
