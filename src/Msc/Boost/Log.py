# ----------------------------------------------------------------------------------
#  Title      : Logging support
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : log.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-07
# ----------------------------------------------------------------------------------
#  Description: Colorized logging support
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import logging
import os
import sys

class Color(object):
    ESC = chr(27)
    green = ESC+"[38;5;2m"
    red = ESC+"[38;5;1m"
    yellow = ESC+"[38;5;11m"
    regular = ESC+"[0m"
    ERROR = red
    WARNING = yellow
    OK = green

COLOR = Color()

# No color support for dumb terminals
USE_COLORS = not (os.environ.get("TERM", "dumb") == "dumb")

def Colorize(color, txt):
    if USE_COLORS:
        return color+txt+COLOR.regular
    else:
        return txt

# For unit testing: allow to force the usage of colors
FORCE_COLORS = False

class MscLogStreamHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        # self.warn_file_stream uses file descriptor 3 when available, otherwise stdout
        # shell% ./1.py 3 > warn_log_file
        try:
            self.warn_file_stream = os.fdopen(3,"w")
        except:
            self.warn_file_stream = sys.stdout

    def emit(self, record):
        # Based on logging.StreamHandler
        try:
            msg = self.format(record)
            msg = "%s: %s" % (logging.getLevelName(record.levelno), msg)
            stream = sys.stdout
            color = None
            if record.levelno == logging.ERROR:
                stream = sys.stderr
                color = COLOR.ERROR
            elif record.levelno == logging.WARNING:
                stream = self.warn_file_stream
                color = COLOR.WARNING
            if color is not None and (stream.isatty() or FORCE_COLORS):
                msg = Colorize(color, msg)
            self.stream = stream

            stream.write(msg)
            stream.write("\n")
            self.flush()
        except Exception:
            self.handleError(record)

def GetLogger(name=None):
    """
    Setup and get a logger.
    """
    name = name or "Main"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    msc_log_handler = MscLogStreamHandler()
    logger.addHandler(msc_log_handler)
    return logger
