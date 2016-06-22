# ----------------------------------------------------------------------------------
#  Title      : Logging tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_Logging.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-07
# ----------------------------------------------------------------------------------
#  Description: Logging tests
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os

import py.io
import pytest

import Msc.Boost

@pytest.fixture("session")
def logger():
    return Msc.Boost.Log()

WARN_FILE_NAME = "test_log_warn.log"

def test_log_redirection(request, logger, capsys):
    # Special handling: Redirect file descriptor 3 output to a file for verification
    capture_warn = py.io.FDCapture(3, open(WARN_FILE_NAME, "wb+"))
    print("")
    logger.warn("logger_warn")
    logger.error("logger_error")
    logger.info("logger_info")
    out, err = capsys.readouterr()
    assert out == "\nINFO: logger_info\n"
    assert err == "ERROR: logger_error\n"
    # py.test -s flag undoes the file descriptor redirection from the logger
    if not request.config.getoption("-s"):
        warn = open(WARN_FILE_NAME).read()
        assert warn == "WARNING: logger_warn\n"
        os.unlink(WARN_FILE_NAME)

def test_log_colors(request, logger, capsys, monkeypatch):
    monkeypatch.setattr(Msc.Boost.Logging, "USE_COLORS", True)
    monkeypatch.setattr(Msc.Boost.Logging, "FORCE_COLORS", True)
    ESC = chr(27)
    red = ESC+"[38;5;1m"
    yellow = ESC+"[38;5;11m"
    regular = ESC+"[0m"
    logger.error("logger_error")
    out, err = capsys.readouterr()
    assert err == red+"ERROR: logger_error"+regular+"\n"
    # py.test -s flag undoes the file descriptor redirection from the logger
    if not request.config.getoption("-s"):
        capture_warn = py.io.FDCapture(3, open(WARN_FILE_NAME, "wb+"))
        logger.warn("logger_warn")
        warn = open(WARN_FILE_NAME).read()
        assert warn == yellow+"WARNING: logger_warn"+regular+"\n"
        os.unlink(WARN_FILE_NAME)

def test_log_accumulation(logger, capsys):
    logger2 = Msc.Boost.Log()
    logger.error("error1")
    logger2.error("error2")
    out, err = capsys.readouterr()
    assert err == "ERROR: error1\nERROR: error2\n"

def test_msc_log(logger, capsys):
    logger.out(0, "Level0 msg")
    logger.out(1, "Level1 msg (is hidden)")
    logger.set_verbosity(1)
    logger.out(1, "Level1 msg#part2")
    out, err = capsys.readouterr()
    assert out == "Level0 msgLevel1 msg#part2"
