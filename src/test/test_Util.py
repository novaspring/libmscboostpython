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

import MscBoost.Util as Util

WORKING_DIR_NAME = "working_dir_test"

def test_working_directory(capsys):
    os.system("rm -fr %s" % WORKING_DIR_NAME)
    os.makedirs(WORKING_DIR_NAME)
    cwd = os.getcwd()
    with Util.WorkingDirectory(WORKING_DIR_NAME):
        os.system("touch readme.txt")
        assert os.getcwd() == os.path.join(cwd, WORKING_DIR_NAME)
    assert os.path.exists(os.path.join(cwd, WORKING_DIR_NAME, "readme.txt"))
    assert os.getcwd() == cwd
    assertion_ok = False
    try:
        with Util.WorkingDirectory(WORKING_DIR_NAME):
            unknown_identifier_error
    except NameError:
        out, err = capsys.readouterr()
        assert err == "Error during processing in 'working_dir_test'\n"
        assertion_ok = True
    assert assertion_ok

def test_timestamped_backup_file(capsys):
    with Util.WorkingDirectory(WORKING_DIR_NAME):
        bak_file_name = Util.make_timestamped_backup_file("readme.txt")
        Util.make_timestamped_backup_file("readme.txt")
        out, err = capsys.readouterr()
        assert err == "WARNING: '%s' does already exist\n" % bak_file_name
        assert Util.make_timestamped_backup_file("readme2.txt") is None
        os.system("touch readme2.txt")
        bak_file_name2 = Util.make_timestamped_backup_file("readme2.txt", keep_old=False)
        assert os.listdir(".") == ["readme.txt", bak_file_name, bak_file_name2]
