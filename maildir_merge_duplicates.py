#!/usr/bin/python
#
#    maildir_merge_duplicates.py
#
#    Removes duplicate emails/files in a maildir and merges their flags.
#
#    Copyright (C) 2009-2021 Georg Lutz <georg AT NOSPAM georglutz DOT de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from optparse import OptionParser
import sys
import hashlib

VERSIONSTRING = "0.1"

# See e.g. http://cr.yp.to/proto/maildir.html
SUPPORTED_MAILDIR_FLAGS = [
	"P", # Flag "P" (passed): the user has resent/forwarded/bounced this message to someone else. 
	"R", # Flag "R" (replied): the user has replied to this message.
	"S", # Flag "S" (seen): the user has viewed this message, though perhaps he didn't read all the way through it.
	"T", # Flag "T" (trashed): the user has moved this message to the trash; the trash will be emptied by a later user action.
	"D", # Flag "D" (draft): the user considers this message a draft; toggled at user discretion.
	"F"  # Flag "F" (flagged): user-defined flag; toggled at user discretion.
	]


class decisionTableEntry:
    def __init__(self):
	self.filesToRemove  = []
	self.fileRenameFrom = ""
	self.fileRenameTo   = ""


def getSize(file):
    statinfo = statinfo = os.stat(file)
    return statinfo.st_size


def calcHash(listEntry):
    for el in listEntry:
	if len(listEntry[el]) == 0:
	    f = file(el,"rb")
	    hash = hashlib.sha1(f.read()).hexdigest()
	    listEntry[el] = hash


def readinDir(path, list):
    '''Reads in files in directory path and constructs a hash table with the
    filelength as key. The value itself consists of a further hash table with
    the path name as key and the sha1 hash as value. The sha1 hash is calculated
    only for file length with more than one entry.
    Example:
    { 2560L: {'/home/gal/Maildir/.gmx/cur/1201719235.M362179P2735V0000000000000806I00090032.ercws055.erc.lan,S=2560:2,RS': ''},
     51712L: {'/home/gal/Maildir/.gmx/cur/1224268572.M882281P2744V0000000000000806I004B893F.ercws055.erc.lan,S=51712:2,S': '736913e91d90e9bff1b1367bb1f5fec1',
     '/home/gal/Maildir/.gmx/new/1224268572.M882281P2744V0000000000000806I004B893F.ercws055.erc.lan,S=51712': '736913e91d90e9bff1b1367bb1f5fec1'},'''
    filelist = os.listdir(path)
    for fname in filelist:
	    fpath = os.path.join(path, fname)
	    size = getSize(fpath)
	    if (fname[0] != ".") and os.path.isfile(fpath) and (size > 0) :
		if list.has_key(size):
		    list[size][fpath] = ""
		    calcHash(list[size])
		else:
		    temp = {}
		    temp[fpath] = ""
		    list[size] = temp


def buildDuplicatesList(listIn, listOut):
    '''Reads listIn created by readinDir and filters out duplicates in such a
    way that listOut contains only entries with the same hash value
    Example:
    [['/home/gal/Maildir/.gmx/cur/1224268572.M882281P2744V0000000000000806I004B893F.ercws055.erc.lan,S=51712:2,S', '/home/gal/Maildir/.gmx/new/1224268572.M882281P2744V0000000000000806I004B893F.ercws055.erc.lan,S=51712']]
    '''
    for keyIn in listIn:
	if len(listIn[keyIn]) > 1:
	    # A temporary dict to determine the duplicate hash values. Key is
	    # the hash value. Value is a list/array of filenames
	    temp = {}
	    # keyIn2 is the filename, listIn[keyIn][keyIn2] is the hash
	    for keyIn2 in listIn[keyIn]:
		if temp.has_key(listIn[keyIn][keyIn2]):
		    temp[listIn[keyIn][keyIn2]].append(keyIn2)
		else:
		    temp2 = []
		    temp2.append(keyIn2)
	            temp[listIn[keyIn][keyIn2]] = temp2
	    for keyTemp in temp:
		if len(temp[keyTemp]) > 1:
		    listOut.append(temp[keyTemp])


def parseMaildirFlags(fileName):
    '''Parses maildir flags encoded in fileName and returns a dict containing
    SUPPORTED_MAILDIR_FLAGS as key and true/false as value'''
    flags = {}
    for entry in SUPPORTED_MAILDIR_FLAGS:
	flags[entry] = False
    posInfo = fileName.find(":2,")
    if posInfo == -1:
	return flags
    i = posInfo + 3
    while i < len(fileName):
	for entry in SUPPORTED_MAILDIR_FLAGS:
	    if entry == fileName[i]:
		flags[entry] = True
	i = i + 1
    return flags


def mergeMaildirFlags(flagsList):
    '''Takes a list of SUPPORTED_MAILDIR_FLAGS (key, value is True/False) and
    returns the merged list'''
    mergedFlags = {}
    i = 0
    while i < len(SUPPORTED_MAILDIR_FLAGS):
	mergedFlags[SUPPORTED_MAILDIR_FLAGS[i]] = False
	i = i + 1
    
    for key in flagsList:
	for key2 in flagsList[key]:
	    if flagsList[key][key2]:
		mergedFlags[key2] = True
	i = i + 1
    return mergedFlags


def setFlagsForMaildirFile(filepath, flags):
    '''Set flags in a maildir filepath. Returns the new filepath with flags.
    flags is a key/value dict of SUPPORTED_MAILDIR_FLAGS. In case of error
    just returns the input parameter filepath.'''
    dirname = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    posInfo = filename.find(":2,")
    if posInfo == -1:
	return filepath

    flagString = ""
    for key in sorted(flags.keys()):
	if flags[key]:
	    flagString = flagString + key
   
    #todo: flagString alphabetisch sortieren
    filenameNew = filename[0:posInfo+3] + flagString
    return os.path.join(dirname, filenameNew)
    

def selectMails(mails, entryOut):
    '''Reads in a list (array) of duplicate mails and fills in entry
    (of type decisionTableEntry)'''
    
    flags = {}
    for entry in mails:
	# flags dict: key is filepath, value is maildir flag dict
	flags[entry] = parseMaildirFlags(os.path.basename(entry))

    # Strategy: Find mail with maximum nr of flags and keep that file
    maxNrOfFlags = 0
    maxNrOfFlagsMail = ""
    for key in flags:
	nrOfFlags = 0
	for key2 in flags[key]:
	    if flags[key][key2]:
		nrOfFlags = nrOfFlags + 1
	if nrOfFlags > maxNrOfFlags:
	    maxNrOfFlags = nrOfFlags
	    maxNrOfFlagsMail = key
    
    mergedFlags = mergeMaildirFlags(flags)
    filePathNew = setFlagsForMaildirFile(maxNrOfFlagsMail, mergedFlags)

    for entry in mails:
	if entry != maxNrOfFlagsMail:
	    entryOut.filesToRemove.append(entry)
    if maxNrOfFlagsMail != filePathNew :
	entryOut.fileRenameFrom = maxNrOfFlagsMail
	entryOut.fileRenameTo = filePathNew
   

def buildDecisionTable(maildirPath, listIn, listOut):
    '''Build a decision table for the found duplicates. listIn is expected to in
    format that buildDuplicatesList has created. The decision table consists of
    an array with elements of type decisionTableEntry.'''

    maildirPathCur = os.path.join(maildirPath, "cur")
    maildirPathNew = os.path.join(maildirPath, "new")

    for keyIn in listIn:

	# First step: If the duplicates are in the new folder we can delete the
	# mails in the new folder and do not need to merge flags as mails in new
	# folder do not have flags by definition.
	entryIn = keyIn
	entryOut = decisionTableEntry()
	mailsInNew = []
	mailsInCur = []
	for keyIn2 in keyIn:
	    if os.path.dirname(keyIn2) == maildirPathCur :
		mailsInCur.append(keyIn2)
	    if os.path.dirname(keyIn2) == maildirPathNew :
		mailsInNew.append(keyIn2)
	
	if len(mailsInNew) > 0:
	    if len(mailsInCur) > 0:
		# delete all in new
		entryOut.filesToRemove = mailsInNew
		selectMails(mailsInCur, entryOut)
	    else:
		# delete all but one in new
		i = 0
		while i < len(mailsInNew):
		    if i < (len(mailsInNew) - 1):
			entryOut.filesToRemove = mailsInNew[i]
		    else:
			entryOut.fileRenameFrom = mailsInNew[i]
			entryOut.fileRenameTo = mailsInNew[i]
		    i = i + 1
	else:
	    selectMails(entryIn, entryOut)
	
	listOut.append(entryOut)


def performActions(list):
    '''Performs actions (i.e. deletes and renames files) defined in list. List
    is expected to be of class decisionTableEntry'''
    for entry in list:
	for fileToRemove in entry.filesToRemove:
	    print "deleting file:"
	    print "  " + fileToRemove
	    print
	    os.remove(fileToRemove)
	if (len(entry.fileRenameFrom) > 0) and (len(entry.fileRenameTo) > 0):
	    print "renaming file:"
	    print "  from " + entry.fileRenameFrom
	    print "  to   " + entry.fileRenameTo
	    print
	    os.rename(entry.fileRenameFrom, entry.fileRenameTo)
	


########### MAIN PROGRAM #############

parser = OptionParser(
	usage="%prog [options] Maildir",
	version="%prog " + VERSIONSTRING + os.linesep +
	"Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de")

parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-w", "--write",
                  action="store_true", dest="write", default=False,
                  help="write changes to filesystem (delete duplicates)")

(options, args) = parser.parse_args()

if len(args) < 1:
    parser.print_help()
    sys.exit(2)

optMaildir = os.path.expanduser(args[0])

maildirPathCur = os.path.join(optMaildir, "cur")
maildirPathNew = os.path.join(optMaildir, "new")


if not os.path.isdir(maildirPathCur) or not os.path.isdir(maildirPathNew):
    print "Maildir cannot be opened"
    sys.exit(1)

filenamesSizes = {}
readinDir(maildirPathCur, filenamesSizes)
readinDir(maildirPathNew, filenamesSizes)


duplicateMails = []
buildDuplicatesList(filenamesSizes, duplicateMails)
decisionTable = []

buildDecisionTable(optMaildir, duplicateMails, decisionTable)


assert( len(duplicateMails) == len(decisionTable) )
i = 0
while i < len(duplicateMails):
    print "[" + str(i) + "]"
    
    print "  duplicate emails:"
    for entry in duplicateMails[i]:
	print "    " + entry
    
    print "  files to remove:"
    for entry in decisionTable[i].filesToRemove:
	print "    " + entry
    
    print "  fileRenameFrom:"
    print "    " + decisionTable[i].fileRenameFrom
    print "  fileRenameTo:"
    print "    " + decisionTable[i].fileRenameTo
    print
    i = i + 1

if options.write:
    print
    print "PERFORMING WRITE OPERATIONS"
    performActions(decisionTable)
    

