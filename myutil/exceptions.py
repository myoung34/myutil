# -*- coding: utf-8 -*-
import sys


class CommandException(Exception):
    sys.tracebacklimit = 0
    pass
