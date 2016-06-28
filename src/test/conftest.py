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
        q.d = pdb.set_trace  # Setup a py.test compatible debug-break function
    except ImportError:
        return
    # Inject q into all test modules
    for module_name, module in sys.modules.items():
        if module_name.startswith("test_"):
            module.q = q
