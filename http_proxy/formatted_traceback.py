# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import traceback as tb
import sys


def formatted_tb():
    """Pretty format the traceback and return a unicode instance."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    formatted = tb.format_exception(exc_type, exc_value, exc_traceback)
    return " ".join([x.decode("utf8") for x in formatted])
