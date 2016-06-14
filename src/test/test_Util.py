# ----------------------------------------------------------------------------------
#  Title      : Util tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_Util.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-14
# ----------------------------------------------------------------------------------
#  Description: Utility function tests
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os

import pytest

import Msc.Boost.Util as Util

def test_working_directory():
    dir_name = "working_dir_test"
    os.system("rm -fr %s" % dir_name)
    os.makedirs(dir_name)
    cwd = os.getcwd()
    with Util.WorkingDirectory(dir_name):
        os.system("touch readme.txt")
        assert os.getcwd() == os.path.join(cwd, dir_name)
    assert os.path.exists(os.path.join(cwd, dir_name, "readme.txt"))
    assert os.getcwd() == cwd
    assertion_ok = False
    try:
        with Util.WorkingDirectory(dir_name):
            unknown_identifier_error
    except NameError:
        assertion_ok = True
    assert assertion_ok
