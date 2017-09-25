# -*- coding: utf-8 -*-
"""
 collector.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys
import traceback

sys.path.append("../..")

from middleware.log import LogManager
from middleware.timer import Timer

from configs import *
from dbbase import DbBase
from task import *


class Collector(DbBase):

    """Collect finance data manager. """

    def __init__(self):
        super(Collector, self).__init__()
        self._logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self._poll_task_time = POLL_TASK_TIME
        self._task_timer = Timer.add_repeat_timer(self._poll_task_time, self._poll_task)
        self._stop_flag = False
        self._current_task = None

    def run(self):
        self._logger.info('init: %s', 'Collector started.')
        while True:
            if self._stop_flag:
                break
            try:
                Timer.loop(0.01)
            except: #ignore all exceptions
                traceback.print_stack()
        Timer.close_all()
        self._logger.info('run: %s', 'Collector stopped.')

    def stop(self):
        self._stop_flag = True

    def _poll_task(self):
        self._db.find(self._task_table, "*", None,
                      callback=lambda flag, result: self._parse_task(result))

    def _parse_task(self, tasks):
        if tasks:
            for task in tasks:
                task_type = task['type']
                self._logger.info('parse_task: %s %s.', 'Run task type ', task_type)

                if task_type == TASK_TYEP['AMERICAN_SHARE_LIST']:
                    self._current_task = TaskAmericanShareList(task)

                elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_HISTORY']:
                    self._current_task = TaskAmericanShareDataHistory(task)

                elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_UPDATE']:
                    self._current_task = TaskAmericanShareDataUpdate(task)

                elif task_type == TASK_TYEP['STOP_BUILDIN_TASK']:
                    self._current_task = TaskStopBuildinTask(task)

                elif task_type == TASK_TYEP['CLEAR_BUILDIN_TASK']:
                    self._current_task = TaskClearBuildinTask(task)

                else:
                    self._logger.warn('parse_task: %s', 'Invalid task type.')
                    continue

                self._current_task.run()

