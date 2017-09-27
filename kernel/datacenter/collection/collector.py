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
from middleware.thread import ThreadPool, WorkRequest

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
        self._run_task_thread_num = RUN_TASK_THREAD_NUM
        self._task_pool = ThreadPool(self._run_task_thread_num)
        self._stop_flag = False

    def run(self):
        self._logger.info('init: %s', 'Collector started.')
        while True:
            if self._stop_flag:
                break
            try:
                Timer.loop(0.01)
            except: #ignore all exceptions
                traceback.print_stack()
        self._logger.info('run: %s', 'Collector stopped.')

    def stop(self):
        self._task_pool.dismissWorkers(self._run_task_thread_num)
        Timer.add_timer(0.5, self._stop)

    def _stop(self):
        Timer.close_all()
        self._stop_flag = True

    def _poll_task(self):
        self._db.find(self._task_table, "*", None,
                      callback=lambda flag, result: self._run_task(result))

    def _run_task(self, tasks):
        if tasks:
            for task in tasks:
                task_entity = self._create_task(task)

                if task_entity:
                    task_status = task['status']
                    request = None

                    if task_status == TASK_STATUS['WAITING']:
                        request = WorkRequest(
                            task_entity.start, (task),
                            callback=lambda requset, result: self._run_task_callback(request, result))

                    elif task_status == TASK_STATUS['INTERRUPTED']:
                        request = WorkRequest(
                            task_entity.resume, (task),
                            callback=lambda requset, result: self._run_task_callback(request, result))

                    else:
                        self._logger.warn('_parse_task: %s %s.', 'Invalid task status', task_status)
                        continue

                    self._task_pool.putRequest(request)

    def _run_task_callback(self, request, result):
        if result == None:
            pass
        elif result == TASK_STATUS['FAILED']:
            pass
        elif result == TASK_STATUS['FINISHED']:
            pass
        else:
            pass

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
