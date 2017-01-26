# ----------------------------------------------------------------------------------
#  Title      : Various utility functions
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : Util.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-14
# ----------------------------------------------------------------------------------
#  Description: Various utility functions
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016-2017 -- MSC Technologies
# ----------------------------------------------------------------------------------

import datetime
import os
import shutil
import sys

class WorkingDirectory(object):
    """
    Change to a working directory and ensure that the old working directory is restored afterwards.
    """
    def __init__(self, directory):
        self.directory = directory
        self.old_dir = os.getcwd()
        os.chdir(directory)
    def __enter__(self):
        return None
    def __exit__(self, type_, value_, traceback_):
        if type_:
            print("Error during processing in '%s'" % self.directory, file=sys.stderr)
        os.chdir(self.old_dir)
        # return False to re-raise an occured exception
        return False

def get_timestamp_string(timestamp=None, file_name_compatible=False):
    """
    Get a timestamp string for the given timestamp. When timestamp is None use the current time.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()
    if file_name_compatible:
        return timestamp.strftime("%Y-%m-%d__%H_%M_%S")
    else:
        return timestamp.strftime("%Y-%m-%d, %H:%M:%S")

def convert_timestamp_string_to_timestamp(timestamp_string, file_name_compatible=False):
    """
    The inverse operation for get_timestamp_string.
    """
    if file_name_compatible:
        return datetime.datetime.strptime(timestamp_string, "%Y-%m-%d__%H_%M_%S")
    else:
        return datetime.datetime.strptime(timestamp_string, "%Y-%m-%d, %H:%M:%S")

def make_timestamped_backup_file(file_name, postfix="", keep_old=True, bak_extension=""):
    """
    Create a backup file. Derive its backup file name from its last modification timestamp.
    """
    if os.path.exists(file_name):
        file_timestamp = datetime.datetime.fromtimestamp(os.stat(file_name).st_mtime)
        TIME_STAMP_FORMAT = "%Y-%m-%d_%H_%M_%S"
        timestamp_string = file_timestamp.strftime(TIME_STAMP_FORMAT)
        file_base_name, file_ext = os.path.splitext(file_name)
        new_file_name = "%s__%s%s%s%s" % (file_base_name, timestamp_string, postfix, file_ext, bak_extension)
        if not os.path.exists(new_file_name):
            if keep_old:
                shutil.copy2(file_name, new_file_name)
            else:
                os.rename(file_name, new_file_name)
        else:
            from .Logging import Log
            Log().warning("'%s' does already exist" % new_file_name)
        return new_file_name

def indent_text(text, indent=2):
    """
    Indent the given text by indent spaces.
    """
    prefix = " "*indent
    result = ""
    for line in text.split("\n"):
        result += "%s%s\n" % (prefix, line)
    return result

def plural_s(decider):
    """
    Return a plural 's' when the length of decider is != 1.
    """
    if type(decider) == int:
        length = decider
    else:
        length = len(decider)
    if length == 1:
        return ""
    else:
        return "s"
