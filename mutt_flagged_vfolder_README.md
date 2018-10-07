# mutt_flagged_vfolder

vFolder in mutt containing all flagged messages from ~/Maildir

Personally I often mark messages which need to be worked on later (effort > 2 minutes in GTD speak) with a flag. As flags are preserved when syncronizing Maildirs over IMAP with offlineimap I can mark them both over IMAP client or locally with mutt.

I have multiple email accounts with a lot of subfolders under my ~/Maildir in Maildir++ format. As mutt currently does not has a concept of virtual folders I cannot have a quick overview of all flagged messages across my Maildir++ folder structure out of the box.

I found a partial solution to this problem in a [LinuxJournal article](http://www.linuxjournal.com/article/10246). It proposed to just create a dummy maildir and symlink flagged messages there, pointing to the real location. As long as you don't alter something in the dummy / virtual folder mutt works quite happy with it. But when you start replying or unflagging in your virtual folder mutt changes the name of the symlink instead of the real message in the source folder and the information gots lost on the next run of the script.

But operating directly in a vfolder isn't a option to me anyway. As I have multiple accounts in my ~/Maildir I heavily use folder hooks to set different from addresses, record folders, PGP options etc.. This all would not work anymore in a central (virtual) folder. So I looked for a solution to quickly jump from a marked message in a virtual folder to the source message in the original folder.

As we use symlinks the source Maildir is already encoded in the filesystem. To jump to a the distinct message inside mutt we search for the message id in the folder like described in the [mutt-open script](http://upsilon.cc/~zack/blog/posts/2009/10/mail_indexing_for_mutt/mutt-open).

Mutt itself isn't really scriptable, but you can use the trick to call an external helper script which does generate a configiration file like ~/.muttrc which can be sourced by mutt in turn, see [here](http://wiki.mutt.org/?ConfigTricks).

Unfourtunatly when mutt calls an external script it is not possible to pass [filename information](http://objectmix.com/mutt/202017-passing-mutt-variables-shell-commands.html). Also when an editor like vim is called a copy of the original file / mail is passed and not the original one. There is an patch to support `<edit-inplace>`, but it is not part of the offical [mutt release]((http://www.steve.org.uk/Software/mutt-tagging/).

So we can just pipe the message out of mutt to our external script. To find the correct symlink in the vfolder we need to parse the mail for the message id and look for a match to it in the vfolder. Of course this is a ugly hack, but the only solution I found so far, without patching mutt...

The generation of the links is done in mutt_flagged_vfolder_link.py. Just provide the Maildir and the path to the vfolder. If vfolder is underneath Maildir it won't be searched itself for flagged messages. To jump to the original message call mutt_flagged_vfolder_jump.py from within mutt.

Of course you will need to adapt your mutt configuration. I use the following:

    folder-hook . 'macro index F "<flag-message><enter-command>unset wait_key^m<sync-mailbox><shell-escape>mutt_flagged_vfolder_link.py ~/Maildir ~/Maildir/.flagged^m<enter-command>set wait_key^m"'

    folder-hook ".*flagged*" 'macro index F "<enter-command>unset wait_key^m<pipe-entry>mutt_flagged_vfolder_jump.py ~/Maildir/.flagged ~/tmp/mutt_flagged_vfolder_jump<enter><enter-command>source ~/tmp/mutt_flagged_vfolder_jump^m<enter-command>set wait_key^m"'

So if you are in the vfolder ~/Maildir/.flagged and press "F" in the index mutt jumps to the original message. I use "F", because it won't make any sense in a vfolder with symlinks anyway. The original behaviour for "F" is restored on any other folder. In my email setup mutt_flagged_vfolder_link.py is fast enough to run it additionally after every flag change.

Additional websites that helped me so far:
* http://upsilon.cc/~zack/blog/posts/2009/10/mail_indexing_for_mutt/
* http://docwhat.gerf.org/2007/10/gtd-and-mutt/
