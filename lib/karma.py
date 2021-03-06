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
import logging
import getpass
from bodhi.models import History

######################################################################
## Logging
######################################################################



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
    def __init__(self, name="", user=None):
        """
        Initialize a history file with interesting information.

        @param name: Name of the history
        """
        self.name = name
        if user == None :
            self.user = getpass.getuser()
        else :
            self.user = user

    def save(self, device, action, result, comment=''):
        """
        Write a history record

        @param device: Concerned device
        @param action: The action effecued on the device
        @param result: The result of the action
        """
        histo = History(device=device, action=action, result=result,
                        comment=comment, user=self.user)
        histo.save()

