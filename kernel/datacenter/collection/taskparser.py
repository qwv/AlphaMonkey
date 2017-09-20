# -*- coding: utf-8 -*-
"""
 taskparser.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DataBaseService
from middleware.log import LogManager

import configs
import datasource

class TaskParser(object):

    """Docstring for TaskParser. """

    def __init__(self, task):
        super(TaskParser, self).__init__(task)
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self.db = DataBaseService.get_service(COLLECTION_DATABASE)
        self.task_table = COLLECTION_TABLES['TASK']['NAME']
        self.task_fields = COLLECTION_TABLES['TASK']['FIELDS']
        self.task = task
        self.buildin_task_table = COLLECTION_TABLES['BUILDIN_TASK']['NAME']
        self.buildin_task_fields = COLLECTION_TABLES['BUILDIN_TASK']['FIELDS']

    def run(self):
        self.task_type = task[self.task_fields.index('type')]


class ParserAmericanShareList(TaskParser):

    """Docstring for ParserList. """

    def __init__(self, task):
        super(ParserAmericanShareList, self).__init__(task)

    def run(self):
        data_source = DataSource()
        task


class ParserAmericanShareDataHistory(TaskParser):

    """Docstring for ParserHistory. """

    def __init__(self, task):
        super(ParserDataHistory, self).__init__(task)

    def run(self):
        pass


class ParserAmericanShareDataUpdate(TaskParser):

    """Docstring for ParserUpdate. """

    def __init__(self, task):
        super(ParserDataUpdate, self).__init__(self, task)

    def run(self):
        pass


class ParserStopBuildinTask(TaskParser):

    """Docstring for ParserStopSubTask. """

    def __init__(self, task):
        super(ParserStopBuildinTask, self).__init__(task)

    def run(self):
        pass


class ParserClearBuildinTask(TaskParser):

    """Docstring for ParserClearSubTask. """

    def __init__(self, task):
        super(ParserClearBuildinTask, self).__init__(task)

    def run(self):
        pass
        
