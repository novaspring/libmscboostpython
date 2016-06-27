# ----------------------------------------------------------------------------------
#  Title      : Logging support
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : Logging.py
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
    dark_cyan = ESC+"[38;5;6m"
    dark_grey = ESC+"[38;5;8m"
    regular = ESC+"[0m"
    ERROR = red
    INFO = dark_cyan
    WARNING = yellow
    DEBUG = dark_grey
    NOTICE = green
    OK = green

COLOR = Color()

# No color support for dumb terminals
USE_COLORS = not (os.environ.get("TERM", "dumb") == "dumb")

def colorize(color, txt):
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
            self.warn_file_stream = os.fdopen(3, "w")
        except:  # pragma: no cover
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
            elif record.levelno == logging.DEBUG:
                color = COLOR.DEBUG
            elif record.levelno == logging.INFO:
                color = COLOR.INFO
            elif record.levelno == logging.NOTICE:
                color = COLOR.NOTICE
            if color is not None and (stream.isatty() or FORCE_COLORS):
                msg = colorize(color, msg)
            self.stream = stream

            stream.write(msg)
            stream.write("\n")
            self.flush()
        except Exception:  # pragma: no cover
            self.handleError(record)

class MscLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super(MscLogger, self).__init__(name, level)
        self.out_level = 0
    def __repr__(self):
        return "<MscLogger %s>" % self.name
    def set_verbosity(self, level):
        self.out_level = level
    def out(self, verbosity_level=0, msg=""):
        if verbosity_level <= self.out_level:
            print(msg, end="")
    def notice(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'NOTICE'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.notice("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.isEnabledFor(logging.NOTICE):
            self._log(logging.NOTICE, msg, args, **kwargs)

LOGGERS = {}
def Log(name=None):
    """
    Setup and get a logger.
    """
    name = name or "Main"
    if name in LOGGERS:
        return LOGGERS[name]
    logging.NOTICE = 25
    logging.addLevelName(logging.NOTICE, "NOTICE")
    logging.setLoggerClass(MscLogger)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    msc_log_handler = MscLogStreamHandler()
    logger.addHandler(msc_log_handler)
    LOGGERS[name] = logger
    return logger
