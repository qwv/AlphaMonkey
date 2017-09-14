# -*- coding: utf-8 -*-
"""
 collector.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DatabaseProxy
from log import LogManager

class Collector(object):

    """Collect finance data manager. """

    def __init__(self):
        """TODO: to be defined1. """
        super(Collector, self).__init__()
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        
    def poll_task(self):
        pass
