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
    # Add MscBoost to sys.path
    sys.path.append(os.path.abspath("../"))

# Called once after all tests are collected
def pytest_collection_modifyitems(session, config, items):
    try:
        import q
    except ImportError:
        return
    # Inject q into all test modules
    for module_name, module in sys.modules.items():
        if module_name.startswith("test_"):
            module.q = q
