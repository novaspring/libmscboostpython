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

import logging
import os

import py.io
import pytest

import MscBoost.Logging

@pytest.fixture("module")
def logger():
    """
    A standard application logger
    """
    return MscBoost.Logging.Log()

WARN_FILE_NAME = "test_log_warn.log"

def test_log_redirection(request, logger, capsys):
    # Special handling: Redirect file descriptor 3 output to a file for verification
    capture3 = py.io.FDCapture(3, open(WARN_FILE_NAME, "wb+"))
    print("")
    logger.warn("logger_warn")
    logger.error("logger_error")
    logger.info("logger_info")
    out, err = capsys.readouterr()
    assert out == "\nINFO: logger_info\n"
    assert err == "ERROR: logger_error\n"
    # py.test -s flag undoes the file descriptor redirection from the logger
    if request.config.getoption("-s") != "no":
        warn = open(WARN_FILE_NAME).read()
        assert warn == "WARNING: logger_warn\n"
        os.unlink(WARN_FILE_NAME)
    capture3.done()

def test_log_warning(capsys, monkeypatch):
    # When MSC_FD3_IS_WARNING_PIPE is unset: warnings are sent to stderr
    monkeypatch.delenv("MSC_FD3_IS_WARNING_PIPE")
    no_fd3_logger = MscBoost.Logging.Log("no_fd3")
    no_fd3_logger.warn("test_log_warning")
    out, err = capsys.readouterr()
    assert err == "WARNING: test_log_warning\n"

def test_log_colors(request, logger, capsys, monkeypatch):
    monkeypatch.setattr(MscBoost.Logging, "FORCE_COLORS", True)
    ESC = chr(27)
    red = ESC+"[38;5;1m"
    yellow = ESC+"[38;5;11m"
    regular = ESC+"[0m"
    monkeypatch.setattr(MscBoost.Logging, "USE_COLORS", False)
    assert MscBoost.Logging.colorize(MscBoost.Logging.Color.yellow, "word") == "word"
    monkeypatch.setattr(MscBoost.Logging, "USE_COLORS", True)
    assert MscBoost.Logging.colorize(MscBoost.Logging.Color.yellow, "word") == yellow+"word"+regular
    logger.error("logger_error")
    out, err = capsys.readouterr()
    assert err == red+"ERROR: logger_error"+regular+"\n"
    # py.test -s flag undoes the file descriptor redirection from the logger
    if request.config.getoption("-s") != "no":
        capture3 = py.io.FDCapture(3, open(WARN_FILE_NAME, "wb+"))
        logger.warn("logger_warn")
        warn = open(WARN_FILE_NAME).read()
        assert warn == yellow+"WARNING: logger_warn"+regular+"\n"
        os.unlink(WARN_FILE_NAME)
        capture3.done()

    info = ESC+"[38;5;6m"
    warning = ESC+"[38;5;11m"
    debug = ESC+"[38;5;8m"
    notice = ESC+"[38;5;2m"
    assert MscBoost.Logging.colorize(MscBoost.Logging.Color.INFO, "word") == info+"word"+regular
    assert MscBoost.Logging.colorize(MscBoost.Logging.Color.WARNING, "word") == warning+"word"+regular
    assert MscBoost.Logging.colorize(MscBoost.Logging.Color.DEBUG, "word") == debug+"word"+regular

    logger.debug("logger_debug_msg")
    logger.info("logger_info_msg")
    logger.notice("logger_notice_msg")
    out, err = capsys.readouterr()
    assert out == debug + "DEBUG: logger_debug_msg" + regular + "\n" + info + "INFO: logger_info_msg" + regular + "\n" + notice + "NOTICE: logger_notice_msg" + regular + "\n"
    assert err == ""

def test_log_accumulation(logger, capsys):
    logger2 = MscBoost.Logging.Log()
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
    assert out == "Level0 msg\nLevel1 msg#part2\n"

def test_log_levels(logger, capsys):
    log_level = logger.getEffectiveLevel()
    assert log_level == logging.DEBUG
    logger.setLevel(logging.CRITICAL)
    logger.critical("critical_msg")
    logger.notice("unseen notice")
    logger.setLevel(log_level)
    out, err = capsys.readouterr()
    assert out == "CRITICAL: critical_msg\n"
