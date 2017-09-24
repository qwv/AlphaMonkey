# -*- coding: utf-8 -*-
"""
 task.py  Generated on 2017-09-20 16:41

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DataBaseService
from middleware.log import LogManager

import configs
import datasource

class Task(object):

    """Docstring for Task. """

    def __init__(self, task):
        super(Task, self).__init__(task)
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self.db = DataBaseService.get_service(COLLECTION_DATABASE)
        self.task_table = COLLECTION_TABLES['TASK']
        self.buildin_task_table = COLLECTION_TABLES['BUILDIN_TASK']
        self.task = task

    def parse(self):
        pass

    def run(self):
        self.task_type = self.task['type']

    def poll_buildin_task(self):
        pass

    def update_status(self, status=None, progress=None):
        expressions = list()
        if status:
            expressions.extend([
                "status",
                self.db.operators['exact'] % self.db.format_string(status)])
        if progress:
            expressions.extend([
                "progress",
                self.db.operators['exact'] % self.db.format_string(progress)])
        if len(expressions) != 0:
            condition = ["id", self.db.operators['exact'] % self.task['id']]
            self.db.update(self.task_table, expressions, condition,
                           callback=lambda flag, result: False)

    def finished(self):
        pass

class TaskAmericanShareList(Task):

    """Docstring for ParserList. """

    def __init__(self, task):
        super(TaskAmericanShareList, self).__init__(task)

    def run(self):
        data_source = DataSource()


class TaskAmericanShareDataHistory(Task):

    """Docstring for ParserHistory. """

    def __init__(self, task):
        super(TaskAmericanShareDataHistory, self).__init__(task)

    def run(self):
        pass


class TaskAmericanShareDataUpdate(Task):

    """Docstring for ParserUpdate. """

    def __init__(self, task):
        super(TaskAmericanShareDataUpdate, self).__init__(self, task)

    def run(self):
        pass


class TaskStopBuildinTask(Task):

    """Docstring for ParserStopSubTask. """

    def __init__(self, task):
        super(TaskStopBuildinTask, self).__init__(task)

    def run(self):
        pass


class TaskClearBuildinTask(Task):

    """Docstring for ParserClearSubTask. """

    def __init__(self, task):
        super(TaskClearBuildinTask, self).__init__(task)

    def run(self):
        pass

