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

    def __init__(self, task):
        super(TaskRunner, self).__init__()
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self.db = DataBaseService.get_service(COLLECTION_DATABASE)
        self.task_table = COLLECTION_TABLES['TASK']
        self.task = task
        
    def update_task_status(self, status = None, progress = None):
        expressions = list()
        if status:
            expressions.extend(["status", self.db.db_client.operators['exact'] % selt.db.db_client.format_string(status)])
        if progress:
            expressions.extend(["progress", self.db.db_client.operators['exact'] % self.db.db_client.format_string(progress)])
        condition = ["id", self.db.db_client.operators['exact'] % self.task[self.task_table['FIELDS'].index('id')]]
        self.db.update(self.task_table['NAME'], expressions, condition, callback = lambda flag, result:False)

    def task_finished(self):
        pass
