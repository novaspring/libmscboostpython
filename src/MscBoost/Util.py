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
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os

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
            print("Error during processing in '%s'" % self.directory)
        os.chdir(self.old_dir)
        # return False to re-raise an occured exception
        return False
