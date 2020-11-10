# ----------------------------------------------------------------------------------
#  Title      : py.test configuration
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : conftest.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-07
# ----------------------------------------------------------------------------------
#  Description: Global py.test configuration
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os
import sys

import pytest

# Called before all tests are run
def pytest_configure(config):
    # Prepend MscBoost to sys.path
    sys.path.insert(0, os.path.abspath("../"))
    os.environ["MSC_FD3_IS_WARNING_PIPE"] = ""

# Called once after all tests are collected
def pytest_collection_modifyitems(session, config, items):
    try:
        import q
        import pdb
        import time
        q.d = pdb.set_trace  # Setup a py.test compatible debug-break function
        q.writer.write("Starting libMscBoostPython tests at: %s" % time.strftime("%c", time.localtime(time.time())))
    except ImportError:
        return
    # Inject q into all test modules
    for module_name, module in sys.modules.items():
        if module_name.startswith("test_"):
            module.q = q

# Fixtures
@pytest.fixture(scope="session")
def ctest_active():
    """
    Tests are run using CTest.
    """
    # CTest starts py.test using python -m pytest ...
    pid = os.getpid()
    cmdline = open("/proc/%d/cmdline" % pid).read()
    return "\x00-m\x00pytest" in cmdline

@pytest.fixture(scope="session")
def docker_test_active():
    """
    Tests are run on docker.
    """
    return os.path.exists("/.dockerenv")

@pytest.fixture(scope="session")
def msc_boost_python_dir():
    """
    Return the path where libMscBoostPython is installed.
    """
    msc_boost_python_directory = os.path.dirname(os.path.dirname(__file__))
    return msc_boost_python_directory
