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

import datetime
import os

import pytest

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
    with pytest.raises(NameError):
        with Util.WorkingDirectory(WORKING_DIR_NAME):
            # pylama:ignore=E0602 undefined name
            unknown_identifier_error
    out, err = capsys.readouterr()
    assert err == "Error during processing in 'working_dir_test'\n"

def test_get_timestamp_string():
    almost_now = datetime.datetime.strptime(Util.get_timestamp_string(file_name_compatible=True), "%Y-%m-%d__%H_%M_%S")
    time_diff = datetime.datetime.now() - almost_now
    assert time_diff.total_seconds() < 5
    almost_now = datetime.datetime.strptime(Util.get_timestamp_string(file_name_compatible=False), "%Y-%m-%d, %H:%M:%S")
    time_diff = datetime.datetime.now() - almost_now
    assert time_diff.total_seconds() < 5

def test_timestamped_backup_file(capsys, ctest_active):
    with Util.WorkingDirectory(WORKING_DIR_NAME):
        bak_file_name = Util.make_timestamped_backup_file("readme.txt")
        Util.make_timestamped_backup_file("readme.txt")
        if not ctest_active:
            # The logger warning isn't shown on stderr when CTest drives the py.test tests
            out, err = capsys.readouterr()
            assert err == "WARNING: '%s' does already exist\n" % bak_file_name
        assert Util.make_timestamped_backup_file("readme2.txt") is None
        os.system("touch readme2.txt")
        bak_file_name2 = Util.make_timestamped_backup_file("readme2.txt", keep_old=False)
        assert os.listdir(".") == ["readme.txt", bak_file_name, bak_file_name2]

def test_indent_text():
    Util.indent_text("abc\ndef") == "  abc\n  def"
    Util.indent_text("abc\ndef", 4) == "    abc\n    def"
