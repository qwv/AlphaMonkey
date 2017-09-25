# -*- coding: utf-8 -*-
"""
 buildintask.py  Generated on 2017-09-22 14:15

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.log import LogManager

import dbbase


class BuildinTask(DbBase):

    """Docstring for BuildinTask. """

    def __init__(self, buildin_task):
        super(BuildinTask, self).__init__(buildin_task)
        self._logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self._buildin_task = buildin_task

    def execute(self):
        pass

    def _check(self):
        pass

    def _remove(self):
        pass
