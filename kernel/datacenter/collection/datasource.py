# -*- coding: utf-8 -*-
"""
 source.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.log import LogManager

import dbbase


class DataSource(DbBase):

    """Docstring for DataSource. """

    def __init__(self):
        super(DataSource, self).__init__()
        self._logger = LogManager.get_logger("collection." + self.__class__.__name__)
        self._source_callback = None

    def get_source(self, source_type, source_callback):
        self._logger.info('get_source: %s.', source_type)
        self._source_callback = source_callback
        condition = ["type", self._db.operators['exact'] % source_type]
        self._db.find(self._task_table, "*", condition,
                      callback=lambda flag, result: self._select_best_source(result))

    def _select_best_source(self, sources):
        best_source = self._find_fastest_source(sources)
        if best_source:
            self._logger.info('select_best_source: %s.', str(best_source))
            self._source_callback(best_source)
        else:
            self._logger.warn('select_best_source: %s', 'Source not found.')
            self._source_callback(None)

    def _find_fastest_source(self, sources):
        #RTT
        return sources[0]

