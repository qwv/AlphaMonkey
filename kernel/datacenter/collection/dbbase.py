# -*- coding: utf-8 -*-
"""
 dbbase.py  Generated on 2017-09-25 16:55

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DataBaseService

from configs import *


class DbBase(object):

    """Docstring for DbBase. """

    def __init__(self):
        super(DbBase, self).__init__()
        self._db = DataBaseService.get_service(COLLECTION_DATABASE)
        self._source_table = COLLECTION_TABLES['SOURCE']
        self._task_table = COLLECTION_TABLES['TASK']
        self._task_history_table = COLLECTION_TABLES['SOURCE']
        self._buildin_task_table = COLLECTION_TABLES['BUILDIN_TASK']

