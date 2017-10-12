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
        self._logger.info('run: %s', 'Collector started.')
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
        if self._current_task:
            self._current_task.interrupt(self._interrupt_task_callback)
        else:
            self._stop_flag = True

    def _poll_task(self):
        # Clear all failed or finished tasks.
        condition = ["status", self._db.operators['exact'] % TASK_STATUS['FAILED'], "OR", 
                     "status", self._db.operators['exact'] % TASK_STATUS['FINISHED']]
        self._db.delete(self._task_table, condition, callback=lambda flag, result: flag)
        # Find an waiting or interrupted task to run.
        if self._current_task is None:
            condition = ["status", self._db.operators['exact'] % TASK_STATUS['WAITING'], "OR", 
                         "status", self._db.operators['exact'] % TASK_STATUS['INTERRUPTED']]
            self._db.findone(self._task_table, "*", condition,
                             callback=lambda flag, result: self._run_task(result))

    def _run_task(self, task):
        if task:
            new_task = self._create_task(task)
            if new_task:
                self._current_task = new_task
                task_status = task['status']

                if task_status == TASK_STATUS['WAITING']:
                    self._current_task.start(self._finish_task_callback)

                elif task_status == TASK_STATUS['INTERRUPTED']:
                    self._current_task.resume(self._finish_task_callback)

    def _create_task(self, task):
        task_type = task['type']
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

    def _interrupt_task_callback(self, flag):
        self._logger.info('_interrupt_task_callback: %s %s.', 'Interrupt task flag', str(flag))
        self._stop_flag = True

    def _finish_task_callback(self, task):
        self._logger.info('_finish_task_callback: %s %s.', 'Finish task sign', task['sign'])
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Ignore task id field.
        task_history = task.values()[1:]
        task_history.append(date_time)
        self._db.insert(self._task_history_table, task_history, lambda flag, result: flag)
        self._current_task = None

