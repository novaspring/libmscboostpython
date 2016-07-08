# ----------------------------------------------------------------------------------
#  Title      : FilePath tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_FilePath.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-07-06
# ----------------------------------------------------------------------------------
#  Description: FilePath tests
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os

from MscBoost.FilePath import FilePath

TEST_FILE_NAME = "test-file-path"
TEST_FILE_NAME2 = "test-file-path2"
def setup_module(module):
    with open(TEST_FILE_NAME, "w") as f:
        f.write("test-123")
    with open(TEST_FILE_NAME2, "w") as f:
        f.write("test-456")

def teardown_module(module):
    os.unlink(TEST_FILE_NAME)
    os.unlink(TEST_FILE_NAME2)

def test_md5():
    fp = FilePath(TEST_FILE_NAME)
    assert fp.md5_hash() == "CA6D00E33EDFF0E9CB3782D31182DE33"
    fp2 = FilePath(TEST_FILE_NAME+"-unknown")
    assert fp2.md5_hash() is None
    assert fp2.md5_check(fp) is False
    assert fp.md5_check(fp) is True

def test_diff_against():
    fp = FilePath(TEST_FILE_NAME)
    fp2 = FilePath(TEST_FILE_NAME2)
    expected_diff = """--- +++ @@ -1 +1 @@-test-123+test-456"""
    assert fp2.diff_against(fp) == expected_diff

