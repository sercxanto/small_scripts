#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
""" sendmail_wrapper.py

    Simple /usr/sbin/sendmail wrapper"""

# The MIT License (MIT)
#
# Copyright (c) 2020 Georg Lutz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Standard library imports:
import configparser
import datetime
import os
import smtplib
import ssl
import sys


class LogToFolder:
    '''Helper class for logging to folder

    Enables logging if logfolder is set'''

    def __init__(self, logfolder):
        self.logfolder = logfolder
        if logfolder:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            prefix = timestamp + "_" + str(os.getpid())
            logfilename_mailin = os.path.join(logfolder, prefix + "_mailin")
            self.logfile_mailin = open(logfilename_mailin, "w")
            self.logfilename_mailout = os.path.join(logfolder, prefix + "_mailout")

    def log_mailin_line(self, line):
        '''Logs a single line'''
        if self.logfolder:
            self.logfile_mailin.write(line)

    def log_mailout(self, message):
        '''Logs the message to file'''
        if self.logfolder:
            with open(self.logfilename_mailout, "w") as file_:
                file_.write(message)

    def __del__(self):
        if self.logfolder:
            self.logfile_mailin.close()


def patch_message(inputfile, from_address, to_address, logfolder):
    '''Patches a system email message so it can be send with most providers.

    Most providers like GMX nowadays have checks in place which check the validity
    of the email message itself, e.g. check the header from/to and compare
    it with the envelope sender. System generated emails like those generated by cron
    might not always conform to it.

    Parameters:

    inputfile: A file like object like stdin
    from_address: The from address which should be set
    to_address: The to address which should be set
    logfolder: If not None logs inputfile content and output string to this folder

    Returns:

    A string which can be send by smtplib.SMTP.sendmail (message whose lines
    are seperated by CRLF).
    '''
    result = ""
    in_header = True
    from_available = False
    to_available = False
    outputlines = []

    log_to_folder = LogToFolder(logfolder)

    for inputline in inputfile:
        log_to_folder.log_mailin_line(inputline)

        # In the header section:
        if in_header:
            if inputline.startswith("From: "):
                outputlines.append("From: " + from_address)
                from_available = True
            elif inputline.startswith("To: "):
                outputlines.append("To: " + to_address)
                to_available = True
            else:
                if inputline.strip():
                    # Still a valid / non empty header line
                    outputlines.append(inputline.strip())
                else:
                    # Empty line: Seperator between header and body
                    if not from_available:
                        outputlines.append("From: " + from_address)
                    if not to_available:
                        outputlines.append("To: " + to_address)
                    outputlines.append("User-Agent: sendmail_wrapper")
                    in_header = False
                    outputlines.append("")
        # In the body section:
        else:
            outputlines.append(inputline.strip())

    for line in outputlines:
        result = result + line + "\r\n"

    log_to_folder.log_mailout(result)

    return result


def log_call(logfolder):
    '''Log the call to the logfolder'''
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    logfile = os.path.join(logfolder, "{}_{}_call".format(timestamp, os.getpid()))
    with open(logfile, "w") as file_:
        ppid = os.getppid()
        file_.write("Parent process ID: {}\n".format(ppid))
        file_.write("UID: {}\n".format(os.getuid()))
        command_file = "/proc/{}/comm".format(ppid)
        command = open(command_file, "r").readline().strip()
        file_.write("parent command: " + command + "\n")


def sendmail_wrapper(inputfile, config):
    '''Main logic of the script

    inputfile: File descriptor for input file
    config: Config as described in read_configfile()
    '''

    if config["logfolder"]:
        log_call(config["logfolder"])

    patched_message = patch_message(
        inputfile, config["from_address"], config["to_address"],
        config["logfolder"])

    connection = smtplib.SMTP(
        host=config["servername"],
        port=config["port"])

    #connection.set_debuglevel(2)

    ssl_context = ssl.create_default_context()

    connection.starttls(context=ssl_context)
    connection.login(
        user=config["username"],
        password=config["password"])
    connection.sendmail(
        from_addr=config["from_address"],
        to_addrs=[config["to_address"]],
        msg=patched_message)

def read_configfile(configfile):
    '''Reads out the config file

    See the README file for the exact format of the config file.

    A likewise dict is returned.
    '''

    config = configparser.ConfigParser()
    with open(configfile, 'r') as file_:
        config_string = '[dummy_section]\n' + file_.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)

    result = {
        "from_address": config["dummy_section"]["from_address"],
        "to_address": config["dummy_section"]["to_address"],
        "servername": config["dummy_section"]["servername"],
        "port": config["dummy_section"]["port"],
        "username": config["dummy_section"]["username"],
        "password": config["dummy_section"]["password"],
        "logfolder": config["dummy_section"].get("logfolder")
    }
    return result


def main():
    '''main function, called when script file is executed directly'''

    scriptname_base = "sendmail_wrapper" # set to a fixed value in case that this script is renamed
    config_env_variable = scriptname_base.upper() + "_CONFIG_FILE"
    config_file = os.getenv(config_env_variable, "/etc/" + scriptname_base + ".ini")

    config = read_configfile(config_file)

    sendmail_wrapper(sys.stdin, config)


if __name__ == "__main__":
    main()