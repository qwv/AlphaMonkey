# -*- coding: utf-8 -*-
"""
 source.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DataBaseService
from middleware.log import LogManager

import configs

class DataSource(object):

    """Docstring for DataSource. """

    def __init__(self):
        super(DataSource, self).__init__()
        self.logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self.db = DataBaseService.get_service(COLLECTION_DATABASE)
        self.source_table = COLLECTION_TABLES['SOURCE']
        self.task_table = COLLECTION_TABLES['TASK']
        self.source_callback = None

    def get_source(self, source_type, source_callback):
        self.logger.info('get_source: %s.', source_type)
        self.source_callback = source_callback
        condition = ["type", self.db.operators['exact'] % source_type]
        self.db.find(self.task_table, "*", condition,
                     callback=lambda flag, result: self.select_best_source(result))

    def select_best_source(self, sources):
        best_source = self.find_fastest_source(sources)
        if best_source:
            self.logger.info('select_best_source: %s.', str(best_source))
            self.source_callback(best_source)
        else:
            self.logger.warn('select_best_source: %s', 'Source not found.')

    def find_fastest_source(self, sources):
        #RTT
        return sources[0]

