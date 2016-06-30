#!/usr/bin/env python3
# ----------------------------------------------------------------------------------
#  Title      : Bootstrap libMscBoostPython example
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : bootstrap_app.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-27
# ----------------------------------------------------------------------------------
#  Description: Download libMscBoostPython when necessary
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import bootstrap_msc_boost_python
bootstrap_msc_boost_python.bootstrap_msc_boost_python()

import MscBoost.Logging as Logging

log = Logging.Log()
log.info("MscBoost is o.k. :-)")
