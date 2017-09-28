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
                Timer.loop(0.01, True, None, 1)
            except KeyboardInterrupt:
                break
            except: #ignore all exceptions
                traceback.print_stack()
        Timer.close_all()
        self._logger.info('run: %s', 'Collector stopped.')

    def stop(self):
        self._interrupt_task()
        self._stop_flag = True

    def _interrupt_task(self):
        if self._current_task is not None:
            self._current_task.interrupt()

    def _poll_task(self):
        if self._current_task is None:
            self._db.find(self._task_table, "*", None,
                          callback=lambda flag, result: self._run_task(result))

    def _run_task(self, tasks):
        if tasks:
            for task in tasks:
                new_task = self._create_task(task['type'])
                if new_task:
                    self._current_task = new_task
                    task_status = task['status']

                    if task_status == TASK_STATUS['WAITING']:
                        self._current_task.start()

                    elif task_status == TASK_STATUS['INTERRUPTED']:
                        self._current_task.resume()

                    break

    def _create_task(self, task_type):
        self._logger.info('_create_task: %s %s.', 'Create task type', task_type)

        if task_type == TASK_TYEP['AMERICAN_SHARE_LIST']:
            return TaskAmericanShareList(task)

        elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_HISTORY']:
            return TaskAmericanShareDataHistory(task)

        elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_UPDATE']:
            return TaskAmericanShareDataUpdate(task)

        elif task_type == TASK_TYEP['STOP_BUILDIN_TASK']:
            return TaskStopBuildinTask(task)

        elif task_type == TASK_TYEP['CLEAR_BUILDIN_TASK']:
            return TaskClearBuildinTask(task)

        else:
            self._logger.warn('_create_task: %s %s.', 'Invalid task type', task_type)
            return None
