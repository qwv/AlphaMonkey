# -*- coding: utf-8 -*-
"""
 configs.py  Generated on 2017-09-19 13:07

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import middleware.settings

COLLECTION_DATABASE = DB_DEFAULT

COLLECTION_TABLES = {
    'SOURCE': 'collection_source',
    # 'FIELDS': ['id', 'type', 'url', 'url_field', 'data_format', 'time_interval']
    'TASK': 'collection_task',
    # 'FIELDS': ['id', 'sign', 'type', 'status', 'progress', 'begin_time']
    'TASK_HISTORY': 'collection_task_history',
    # 'FIELDS': ['id', 'sign', 'type', 'status', 'progress', 'begin_time', 'end_time']
    'BUILDIN_TASK': 'collection_buildin_task',
    # 'FIELDS': ['id', 'sign', 'action', 'content']
}

POLL_TASK_TIME = 60 #Second

TASK_TYEP = {
    'AMERICAN_SHARE_LIST': 'asl',#'american share list',
    'AMERICAN_SHARE_DATA_HISTORY': 'asdh',#'american share data history',
    'AMERICAN_SHARE_DATA_UPDATE': 'asdu',#'american share data update',
    'STOP_BUILDIN_TASK': 'sbt',#'stop buildin task',
    'CLEAR_BUILDIN_TASK': 'cbt',#'clear buildin task',
}

TASK_STATUS = {
    'WAITING': 'waiting',
    'PREPARING': 'preparing',
    'PROCESSING': 'processing',
    'INTERRUPTED': 'interrupted',
    'FINISHED': 'finished',
}

