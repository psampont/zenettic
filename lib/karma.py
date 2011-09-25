#!/usr/bin/env python
# karma.py : Device functions

"""
Functions to write history logs.
"""
__docformat__ = 'epytext en'

######################################################################
## Imports
######################################################################

import os
from bodhi.models import History

######################################################################
## Logging
######################################################################

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("lib-history").addHandler(h)

######################################################################
##
######################################################################

class Karma:
    """
    History database
    """
    def __init__(self, name=""):
        """
        Initialize a history file with interesting information.

        @param name: Name of the history
        """
        self.name = name

    def save(self, device, action, result, comment=None):
        """
        Write a history record

        @param device: Concerned device
        @param action: The action effecued on the device
        @param result: The result of the action
        """
        histo = History(device=device, action=action, result=result, comment=comment)
        histo.save()

