# -*- coding: utf-8 -*-
"""
 taskrunner.py  Generated on 2017-09-20 16:41

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DataBaseService
from middleware.log import LogManager
from middleware.timer import Timer

class TaskRunner(object):

    """Docstring for TaskRunner. """

    def __init__(self):
        super(TaskRunner, self).__init__()
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self.db = DataBaseService.get_service(COLLECTION_DATABASE)
        
    def update_task_status(self):
        expressions = ["status", self.db.db_client.operators['exact'] % "''",
                       "progress", self.db.db_client.operators['exact'] % "''",
                       "begin_time", self.db.db_client.operators['exact'] %"''"]
        condition = ["id", self.db.db_client.operators['exact'] % self.task['id']]
        self.db.update(self.task_table, expressions, condition, callback = lambda flag, result:flag)

    def task_finished(self):
        pass
