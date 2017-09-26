# -*- coding: utf-8 -*-
"""
 task.py  Generated on 2017-09-20 16:41

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.log import LogManager

from configs import *
from dbbase import DbBase
from datasource import DataSource
from buildintask import BuildinTask


class Task(DbBase):

    """Docstring for Task. """

    def __init__(self, task):
        super(Task, self).__init__(task)
        self._logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self._task = task
        self._logger.info('__init__: %s %s.', 'Init task', str(self._task))

    def start(self):
        self._logger.info('start: %s %d.', 'Start task sign', self._task['sign'])
        self._update_status(TASK_STATUS['PREPARING'])
        self._data_source = DataSource()
        self._data_source.get_source(self._task['type'], self._source_callback)

    def resume(self):
        self._logger.info('resume: %s %d.', 'Resume task sign', self._task['sign'])
        self._poll_buildin_task()

    def _source_callback(self, source):
        if source:
            self._source = source
            self._parse()
        else:
            self._logger.warn('_source_callback: %s', 'Get source failed.')
            self._failed()

    def _parse(self):
        pass

    def _parse_callback(self, flag):
        if flag:
            self._update_status(TASK_STATUS['PROCESSING'])
            self._poll_buildin_task()
        else:
            self._logger.warn('_parse_callback: %s', 'Parse failed.')
            self._failed()

    def _poll_buildin_task(self):
        self._db.find(self._buildin_task_table, "*", None,
                      callback=lambda flag, result: self._execute_buildin_task(flag, result))

    def _execute_buildin_task(self, flag, result):
        if flag:
            if result:
                buildin_task = BuildinTask(result)
                buildin_task.execute(self._buildin_task_callback)
            else:
                self._finished()
        else:
            self._logger.warn('_execute_buildin_task: %s', 'Poll buildin task failed.')
            self._poll_buildin_task()

    def _buildin_task_callback(self, flag):
        if flag:
            self._update_status(TASK_STATUS['PROCESSING'])
        else:
            self._logger.warn('_buildin_task_callback: %s', 'Execute buildin task failed.')
        self._poll_buildin_task()

    def _failed(self):
        self._update_status(TASK_STATUS['FAILED'])
        self._logger.info('_failed: %s %d.', 'Run task failed sign', self._task['sign'])

    def _finished(self):
        self._update_status(TASK_STATUS['FINISHED'])
        self._logger.info('_finished: %s %d.', 'Run task finished sign', self._task['sign'])

    def _update_status(self, status=None, progress=None):
        expressions = list()
        if status:
            expressions.extend([
                "status",
                self._db.operators['exact'] % self._db.format_string(status)])
        if progress:
            expressions.extend([
                "progress",
                self._db.operators['exact'] % self._db.format_string(progress)])
        if expressions:
            condition = ["id", self._db.operators['exact'] % self._task['id']]
            self._db.update(self._task_table, expressions, condition,
                            callback=lambda flag, result: False)


class TaskAmericanShareList(Task):

    """Docstring for ParserList. """

    def __init__(self, task):
        super(TaskAmericanShareList, self).__init__(task)

    def _parse(self):
        super(TaskAmericanShareList, self)._parse()


class TaskAmericanShareDataHistory(Task):

    """Docstring for ParserHistory. """

    def __init__(self, task):
        super(TaskAmericanShareDataHistory, self).__init__(task)

    def _parse(self):
        super(TaskAmericanShareDataHistory, self)._parse()


class TaskAmericanShareDataUpdate(Task):

    """Docstring for ParserUpdate. """

    def __init__(self, task):
        super(TaskAmericanShareDataUpdate, self).__init__(self, task)

    def _parse(self):
        super(TaskAmericanShareDataUpdate, self)._parse()


class TaskStopBuildinTask(Task):

    """Docstring for ParserStopSubTask. """

    def __init__(self, task):
        super(TaskStopBuildinTask, self).__init__(task)

    def _parse(self):
        super(TaskStopBuildinTask, self)._parse()


class TaskClearBuildinTask(Task):

    """Docstring for ParserClearSubTask. """

    def __init__(self, task):
        super(TaskClearBuildinTask, self).__init__(task)

    def _parse(self):
        super(TaskClearBuildinTask, self)._parse()

