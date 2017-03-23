#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn <r>
# GNU GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html>

"""
__init__.py
.. module:: neat
    :platform: Linux, MacOSX, Win32
    :synopsis:
    :created: 02-16-2017 15:16:19
    :modified: 02-16-2017 15:16:19
.. moduleauthor:: Stephen Bunn <r>
"""

import sys
import inspect

from . import _common
from .obvius import ObviusTranslator


def get_translator(requester_name):
    for (translator_name, translator) in inspect.getmembers(
        sys.modules[__name__], inspect.isclass
    ):
        if requester_name in translator.supported_requesters:
            return translator
