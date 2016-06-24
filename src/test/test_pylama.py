# ----------------------------------------------------------------------------------
#  Title      : pylama tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_pylama.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-24
# ----------------------------------------------------------------------------------
#  Description: pylama test integration
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os
import subprocess

import MscBoost.Util as Util

def get_pylama_ini():
    return os.path.abspath("../../../msc_cmake_scripts/src/msc_pylama.ini")

def run_pylama(directory=".", pattern="*.py"):
    cmd = "pylama --option %s %s" % (get_pylama_ini(), pattern)
    with Util.WorkingDirectory(directory):
        st, out = subprocess.getstatusoutput(cmd)
        if st != 0:
            print("%s: '%s' failed:" % (os.getcwd(), cmd))
            print(out)
    assert st == 0


def test_pylama():
    # Test single file:
    run_pylama(pattern="test_pylama.py")
    # 24.06.2016: TODO: activate the tests below
    # run_pylama(".")
    # run_pylama("../MscBoost")
