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

def test_md5():
    test_file_name = "test-file-path"
    with open(test_file_name, "w") as f:
        f.write("test-123")
    fp = FilePath(test_file_name)
    assert fp.md5_hash() == "CA6D00E33EDFF0E9CB3782D31182DE33"
    fp2 = FilePath(test_file_name+"-unknown")
    assert fp2.md5_hash() is None
    assert fp2.md5_check(fp) is False
    assert fp.md5_check(fp) is True
    os.unlink(test_file_name)
