#!/usr/bin/python
# vim: set fileencoding=utf-8 :
""" start_firefox_cleanprofile.py
    Starts firefox with an empty (clean) profile"""

# The MIT License (MIT)
#
# Copyright (c) 2016 Georg Lutz
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

from __future__ import print_function

# Standard library imports:
import argparse
import os
import platform
import shutil
import subprocess
import sys
import configparser

from future import standard_library
standard_library.install_aliases()


def get_args():
    '''Configures command line parser and returns parsed parameters'''
    parser = argparse.ArgumentParser(
        description="Starts firefox with an empty (clean) profile")
    parser.add_argument("--profile", help="profile name", default="clean")
    return parser.parse_args()


def get_profiles_folder():
    '''Returns platform specific folder where profile.ini is stored'''
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox")
    elif system == "Linux":
        return os.path.join(os.environ["HOME"], ".mozilla", "firefox")
    else:
        raise NameError("Unsupported platform")


def get_clean_profile_folder(profiles_folder, profilename):
    '''Parses profile.ini and returns absolute path to the profile

    Args:
        profile_ini: Full path to the profile.ini file
        profilename: Name of the profile
    Returns:
        Absolute path to the profile directory with the given name

    '''
    profile_path = ""
    config = configparser.RawConfigParser()
    profiles_ini = os.path.join(profiles_folder, "profiles.ini")
    config.read(profiles_ini)
    config.sections()
    for section in config.sections():
        if section.startswith("Profile"):
            if config.get(section, "Name") == profilename:
                profile_path = config.get(section, "Path")
    if len(profile_path) > 0:
        return os.path.join(profiles_folder, profile_path)
    else:
        print("I could read out the profiles.ini file at " + profiles_ini + ".")
        print("But I couldn't find a profile with the name " + profilename + ".")
        print("Please create one with \"firefox --ProfileManager\" as I do not support")
        print("profile creation of my own.")
        sys.exit(1)


def get_executable_path():
    '''Returns executable path based on guess'''
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ["ProgramFiles(x86)"], "Mozilla Firefox", "firefox.exe")
    elif system == "Linux":
        return "/usr/bin/firefox"
    else:
        raise NameError("Unsupported platform")


def start_clean(profilename):
    '''Starts with the given profile name'''
    clean_profile_folder = get_clean_profile_folder(get_profiles_folder(), profilename)
    print("profile folder: " + clean_profile_folder)
    shutil.rmtree(clean_profile_folder)
    os.mkdir(clean_profile_folder)
    executable_path = get_executable_path()
    subprocess.Popen([executable_path, "-P", profilename, "--no-remote"])


def main():
    '''main function, called when script file is executed directly'''
    args = get_args()
    start_clean(args.profile)


if __name__ == "__main__":
    main()

