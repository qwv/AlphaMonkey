# -*- coding: utf-8 -*-
"""
 dbcreator.py

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

import sys

sys.path.append("../..")

from middleware.db import DatabaseProxy
from middleware.settings import *


DATABASE_CREATE_TABLES_DEFAULT = [
    {
        'table': 'collection_source',
        'columns': [ 
            {
                'name': 'id',
                'type': 'UUIDField',
                'describe': 'primary key'
            },
            {
                'name': 'type',
                'type': 'TextField',
            },
            {
                'name': 'url',
                'type': 'TextField',
            },
            {
                'name': 'url_field',
                'type': 'TextField',
            },
            {
                'name': 'data_format',
                'type': 'TextField',
            },
            {
                'name': 'time_interval',
                'type': 'FloatField',
            },
        ],
    },
    {
        'table': 'collection_task',
        'columns': [ 
            {
                'name': 'sign',
                'type': 'IntegerField',
            },
            {
                'name': 'type',
                'type': 'TextField',
            },
            {
                'name': 'status',
                'type': 'TextField',
            },
            {
                'name': 'progress',
                'type': 'FloatField',
            },
            {
                'name': 'begin_time',
                'type': 'DateTimeField',
            },
            {
                'name': 'finish_time',
                'type': 'DateTimeField',
            },
        ],
    },
    {
        'table': 'collection_task_history',
        'columns': [ 
            {
                'name': 'sign',
                'type': 'IntegerField',
            },
            {
                'name': 'type',
                'type': 'TextField',
            },
            {
                'name': 'status',
                'type': 'TextField',
            },
            {
                'name': 'progress',
                'type': 'FloatField',
            },
            {
                'name': 'begin_time',
                'type': 'DateTimeField',
            },
            {
                'name': 'finish_time',
                'type': 'DateTimeField',
            },
        ],
    },
    {
        'table': 'collection_buildin_task',
        'columns': [ 
            {
                'name': 'sign',
                'type': 'IntegerField',
            },
            {
                'name': 'action',
                'type': 'TextField',
            },
            {
                'name': 'content',
                'type': 'TextField',
            },
        ],
    },
]

def db_create_tables(db_name, tables):
    """TODO: create tables for database. """
    db = DatabaseProxy(DATABASES[db_name]['ENGINE'], DATABASES[db_name]['CONFIG'])
    for tb in tables:
        table = tb['table']
        columns = []
        for col in tb['columns']:
            column = col['name'] + " " + db.db_client.data_types[col['type']] + " " 
            column += (col.has_key('describe') and col['describe'] or "")
            columns.append(column)
        db.create_table(table, columns)


if __name__ == "__main__":
    db_create_tables("default", DATABASE_CREATE_TABLES_DEFAULT)

