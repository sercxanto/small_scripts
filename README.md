# small_scripts

Simple scripts to small for own repo:

* `backup_hosted_nextcloud_database.sh`: Backs up nextcloud calendar and addressbooks
* `check_video_length.sh`: Checks video files in a folder to have a minimal length
* `docker_socket_execute.py`: Run "docker exec" commands on a local docker socket without docker client
* `encryptfolder.sh`: Encrypts and signs a folder to a tar.gpg file
* `export_encrypted_borgbackup.sh`: Exports an encrypted borg backup to a tar.gpg file
* `export_encrypted_borgmaticbackup.sh`: Exports an encrypted borgmatic backup to a tar.gpg file
* `find_orphaned_sidecar_files.py`: Find sidecar files (like XMP) which don't have the associated base file anymore
* `get_clip_list.py`: Generates a CSV list of video files
* `maildir_trash.sh`: Purge mails older than 30 days from Maildir trash folder
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

## docker_socket_execute.py

This script emulates a `docker exec ...` call in constraint environments where only 
the socket `/var/run/docker.sock` and a python interpreter is available, e.g.
in a docker container itself without a docker client.

To run `command` in `container` this call

```shell
docker_socket_execute.py container command
```

is equivalent to this one:

```shell
docker exec container command
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


## offlineimap_refresh

[offlineimap](http://www.offlineimap.org/) is a python based tool to synchronize a remote IMAP mailbox to a local Maildir folder structure. Usually it is started in background and starts the synchronization in regular intervals (`autorefresh` setting). If the offlineimap receives a SIGUSR signal it manually triggers the synchronisation as soon as possible. This is exactly what `offlineimap_refresh.sh` is doing.


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
