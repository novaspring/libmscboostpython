# ----------------------------------------------------------------------------------
#  Title      : FilePath class
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : FilePath.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-07-06
# ----------------------------------------------------------------------------------
#  Description: FilePath class
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import difflib
import hashlib

from pathlib import PosixPath


class FilePath(PosixPath):
    def md5_hash(self):
        """
        Get the md5 hash for the handled file - or None when the file does not exist
        """
        try:
            str_ = self.open("rb").read()
            my_hash = hashlib.md5(str_).hexdigest().upper()
        except:
            return None
        return my_hash

    def md5_check(self, other_filepath):
        """
        Perform a hash check to compare the two files
        @param other_filepath: the file to compare to
        @type other_filepath: FilePath
        """
        my_hash = self.md5_hash()
        their_hash = other_filepath.md5_hash()

        return my_hash == their_hash

    def diff_against(self, other_filepath):
        """
        Calculate the unified diff to transform this file content to the other file content.
        """
        my_lines = self.open("r").readlines()
        other_lines = other_filepath.open("r").readlines()
        return "".join(difflib.unified_diff(other_lines, my_lines, lineterm=''))
