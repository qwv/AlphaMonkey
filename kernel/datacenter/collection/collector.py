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

import dbbase
import configs
import taskparser


class Collector(DbBase):

    """Collect finance data manager. """

    def __init__(self):
        super(Collector, self).__init__()
        self._logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self._poll_task_time = POLL_TASK_TIME
        self._task_timer = Timer.add_repeat_timer(self._poll_task_time, self._poll_task)
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
                task_parser = None
                task_type = task['type']
                self._logger.info('parse_task: %s %s.', 'Run task type ', task_type)

                if task_type == TASK_TYEP['AMERICAN_SHARE_LIST']:
                    task_parser = ParserAmericanShareList(task)

                elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_HISTORY']:
                    task_parser = ParserAmericanShareDataHistory(task)

                elif task_type == TASK_TYEP['AMERICAN_SHARE_DATA_UPDATE']:
                    task_parser = ParserAmericanShareDataUpdate(task)

                elif task_type == TASK_TYEP['STOP_BUILDIN_TASK']:
                    task_parser = ParserStopBuildinTask(task)

                elif task_type == TASK_TYEP['CLEAR_BUILDIN_TASK']:
                    task_parser = ParserClearBuildinTask(task)

                else:
                    self.logger.warn('parse_task: %s', 'Invalid task type.')
                    continue

                task_parser.run()

