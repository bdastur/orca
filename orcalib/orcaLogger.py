#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging


class OrcaLogger(object):
    """Builder Logging facility"""

    logLevel = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(
        self,
        name=__name__,
        logFile="/tmp/orcalog.txt",
        fileLogLevel="DEBUG",
        consoleLogLevel="DEBUG",
    ):
        """Initilize Logger
        @args:
            :type name: String
            :param name: Name of the module
            :type logFile: String
            :param logFile: path to the logfile
        """
        if hasattr(OrcaLogger, 'logger'):
            self.logger = OrcaLogger.logger
            print("Orca Logger")
            self.logger.debug("Logger already initialize!")
            return

        # Check if logfile exists
        if not os.path.exists(os.path.dirname(logFile)):
            print("Cannot initialize logger. Path [%s] does not exist"
                  % (os.path.dirname(logFile)))
            return

        formatStr = "[%(asctime)s %(levelname)5s" " %(process)d %(name)s]: %(message)s"
        logging.basicConfig(
            level=OrcaLogger.logLevel[fileLogLevel],
            format=formatStr,
            datefmt="%m-%d-%y %H:%M",
            filename=logFile,
            filemode="a",
        )

        # Define a stream handler for critical errors.
        console = logging.StreamHandler()
        level = OrcaLogger.logLevel[consoleLogLevel]
        console.setLevel(level)

        formatter = logging.Formatter(
            "[%(asctime)s %(levelname)5s %(name)s]: %(message)s",
            datefmt="%m-%d-%y %H:%M",
        )
        console.setFormatter(formatter)

        # Add handler to root logger.
        logging.getLogger(name).addHandler(console)
        self.logger = logging.getLogger(name)
        OrcaLogger.logger = self.logger
        print("Orca Logger initialized")



# --- begin "pretty"
#
# pretty - A miniature library that provides a Python print and stdout
# wrapper that makes colored terminal text easier to use (e.g. without
# having to mess around with ANSI escape sequences). This code is public
# domain - there is no license except that you must leave this header.
#
# Copyright (C) 2008 Brian Nez <thedude at bri1 dot com>
#
# http://nezzen.net/2008/06/23/colored-text-in-python-using-ansi-escape-sequences/

codeCodes = {
    'black':     '0;30', 'bright gray':    '0;37',
    'blue':      '0;34', 'white':          '1;37',
    'green':     '0;32', 'bright blue':    '1;34',
    'cyan':      '0;36', 'bright green':   '1;32',
    'red':       '0;31', 'bright cyan':    '1;36',
    'purple':    '0;35', 'bright red':     '1;31',
    'yellow':    '0;33', 'bright purple':  '1;35',
    'dark gray': '1;30', 'bright yellow':  '1;33',
    'normal':    '0'
}


def stringc(text, color):
    """String in color."""
    return "\033["+codeCodes[color]+"m"+text+"\033[0m"

# --- end "pretty"
