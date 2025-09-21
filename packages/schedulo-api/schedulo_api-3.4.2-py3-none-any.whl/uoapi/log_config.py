"""
Logging configuration and utilities for the uoapi application.

This module provides standardized logging configuration with optional
color support, file logging, and command-line argument integration.
"""

import logging
import logging.handlers
import os
import time
import traceback as tb
import argparse
import json
from copy import copy

logger = logging.getLogger(__name__)

FORMAT_NO_COLOURS = {
    "CRITICAL": "CRITICAL",
    "ERROR": "ERROR   ",
    "WARNING": "WARNING ",
    "INFO": "INFO    ",
    "DEBUG": "DEBUG   ",
}
try:
    import colorama

    colorama.init()
except Exception:
    USE_COLOUR = False
    FORMAT_COLOURS = FORMAT_NO_COLOURS
else:
    USE_COLOUR = True
    FORMAT_COLOURS = {
        "CRITICAL": colorama.Fore.MAGENTA + "CRITICAL" + colorama.Fore.RESET,
        "ERROR": colorama.Fore.RED + "ERROR   " + colorama.Fore.RESET,
        "WARNING": colorama.Fore.YELLOW + "WARNING " + colorama.Fore.RESET,
        "INFO": colorama.Fore.GREEN + "INFO    " + colorama.Fore.RESET,
        "DEBUG": colorama.Fore.BLUE + "DEBUG   " + colorama.Fore.RESET,
    }
FORMAT_COLOURS["WARN"] = FORMAT_COLOURS["WARNING"]
FORMAT_COLOURS["FATAL"] = FORMAT_COLOURS["CRITICAL"]

LOG_LEVELS = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}


class ColouredFormatter(logging.Formatter):
    """
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """

    def __init__(self, fmt=None, datefmt=None, style="%", use_colour=False):
        super().__init__(fmt, datefmt, style)
        self.use_colour = USE_COLOUR and use_colour

    def format(self, record):
        """Format a log record with optional color formatting."""
        record = copy(record)
        if record.levelname in FORMAT_COLOURS:
            if self.use_colour:
                record.levelname = FORMAT_COLOURS[record.levelname]
            else:
                record.levelname = FORMAT_NO_COLOURS[record.levelname]
        record = super().format(record)
        if self.use_colour:
            asctime, record = record.split("::", 1)
            asctime = colorama.Fore.CYAN + asctime + colorama.Fore.RESET
            record = asctime + "::" + record
        return record


class ExceptionTracebackFormatter(logging.Formatter):
    """Formatter that handles exception tracebacks in JSON format."""

    def format(self, record):
        """Format a log record with exception information in JSON format."""
        record = copy(record)
        if record.exc_info is not None:
            info = record.exc_info
            if record.exc_text is not None:
                traceback = record.exc_info
            else:
                traceback = "".join(tb.format_exception(*info))
            record.traceback = json.dumps(traceback).strip('"')
            record.exception = json.dumps(repr(info[1])).strip('"')
            record.exc_info = record.exc_text = None
        else:
            record.exception = record.traceback = ""
        record.msg = json.dumps(record.msg).strip('"')
        return super().format(record)

    def formatException(self, exc_info=None):
        """Return empty string to suppress default exception formatting."""
        return ""


def configure_logging(args):
    """
    :param logdir: directory to put logfiles (defaults to ./)
    :param logname: name of logfiles; "log" if not given;
        ".log" appended if missing
    :param verbosity: {}
    :param use_colour: whether to colour terminal output;
        if colorama is not installed, is silently ignored
    """.format(
        ", ".join(
            "{}->{}".format(k if k != 0 else "default", logging.getLevelName(v))
            for k, v in LOG_LEVELS.items()
        )
    )
    logdir = args.logdir
    logname = args.logname
    verbosity = args.verbosity if not args.quiet else None
    use_colour = (not args.monochrome) and args.color

    logging.Formatter.converter = time.gmtime
    handlers = []

    if os.path.isdir(logdir):
        if isinstance(logname, str) and logname != "":
            logname = logname.rstrip(".log") + ".log"
        else:
            logname = "log"
        logfile = logging.handlers.TimedRotatingFileHandler(
            os.path.join(logdir, logname),
            when="midnight",
            utc=True,
        )
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(
            ExceptionTracebackFormatter(
                json.dumps(
                    {
                        "time": "%(asctime)s",
                        "level": "%(levelname)s",
                        "module": "%(module)s",
                        "pathname": "%(pathname)s",
                        "function": "%(funcName)s",
                        "lineno": "%(lineno)s",
                        "processno": "%(process)d",
                        "threadno": "%(thread)d",
                        "message": "%(message)s",
                        "exception": "%(exception)s",
                        "traceback": "%(traceback)s",
                    }
                ),
                "%Y-%m-%dT%H:%M:%S%Z",
            )
        )
        handlers.append(logfile)

    if verbosity in LOG_LEVELS:
        console = logging.StreamHandler()
        console.setLevel(LOG_LEVELS[verbosity])
        console.setFormatter(
            ColouredFormatter(
                fmt="%(asctime)s :: %(levelname)s "
                + ":: [%(filename)s:%(funcName)s:%(lineno)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                use_colour=use_colour,
            )
        )
        handlers.append(console)
    elif len(handlers) == 0:
        handlers.append(logging.NullHandler())

    logging.basicConfig(level=0, handlers=handlers)


def configure_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",  # This allows for `-vv`-style usage
        dest="verbosity",
        default=0,
        help="Set verbosity level: "
        + ", ".join(
            "{}->{}".format(k if k != 0 else "default", logging.getLevelName(v))
            for k, v in LOG_LEVELS.items()
        ),
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress logging output to stderr",
    )
    parser.add_argument(
        "-l",
        "--logdir",
        action="store",
        default="",
        help="Set destination directory for log files",
    )
    parser.add_argument(
        "--logname", action="store", default="", help="Set name prefix for log files"
    )
    parser.add_argument(
        "-C",
        "--color",
        action="store_true",
        default=False,
        help="Colour terminal output",
    )
    parser.add_argument(
        "-M",
        "--monochrome",
        action="store_true",
        default=False,
        help="Force terminal output to monochrome (overrides -C/--color)",
    )
    return parser


def cause_problems():
    return 1 / 0


def main():
    logging.debug("This is debug")
    logging.info("This is info")
    logging.warning("this is a warning")
    logging.error("This is error")
    logging.critical("This is critical")
    try:
        cause_problems()
    except Exception as e:
        logging.exception(repr(e))
    logging.debug("That's all, folks!")


if __name__ == "__main__":
    args = configure_parser().parse_args()
    configure_logging(args)
    main()
