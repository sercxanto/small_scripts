# Archived scripts

I am not using gnucash anymore. The homebanking CSV conversion scripts are now in an own
project: [go-homebank-csv](https://github.com/sercxanto/go-homebank-csv/).

Therefor the following finance / homebanking scripts are archived:

- `barclaycard2homebank`: Convert barclaycard visa excel transaction report to homebank CSV format
- `moneywallet2homebank`: Convert moneywallet CSV to homebank CSV format
- `fiducia2homebank.py`: Convert the CSV export of fiducia driven banking websites,
    i.e. Volksbank to homebank csv format
- `fix_comdirect_csv.py`: Fix the CSV export of comdirect bank
- `fix_fiducia_csv.py`: Fix the CSV export of fiducia driven banking websites
- `paypal2homebank.py`: Convert the CSV export of paypal to homebank CSV format
- `gnucash_accounts.py`: Get list of accounts from gnucash
- `gnucash_import.py`: Yet another import script for gnucash

My mail setup changed. These were related to old setup or one-time-scripts for migration and fixing issues:

- `maildir_merge_duplicates.py`: I created this Python 2 script to fix a file sync issue
- `msmtpq_notify.py`: Notifies desktop user if msmtpq has actually sent or enqueued mail
- `mutt_flagged_vfolder_jump.py`: Generates mutt command file to jump to the source of a symlinked mail
- `mutt_flagged_vfolder_link.py`: Searches flagged mails and symlinks them to a (vfolder) maildir
- `smtpcheckaddresses.py`: Checks list of mail addresses at mail server
- `sendmail_wrapper.py`: `/usr/sbin/sendmail` replacement for systems without an own local mail server

I am not using duplicity any longer:

- `copy_duplicity_backups.py`: Copies most recent duplicity backup files

## fiducia2homebank

`fiducia2homebank.py` converts the CSV export of fiducia based banking websites (e.g. Volksbank ) to the [CSV import format](http://homebank.free.fr/help/misc-csvformat.html) of [homebank](http://homebank.free.fr).

Example:

```shell
$ fiducia2homebank.py Umsaetze_DExxxxxxxxxxxxxx_2020.01.01.csv ~/out.csv
Found header in line 9
Data section ends in line 42
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
