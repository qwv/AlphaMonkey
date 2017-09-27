# -*- coding: utf-8 -*-
"""
 sleep.py  Generated on 2017-09-27 09:57

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""


import sys
import time
import datetime

sys.path.append("..")

from middleware.http import AsyncHTTPClient, HttpRequest 
from middleware.db import DataBaseService
from middleware.settings import *
from middleware.timer import Timer

client = AsyncHTTPClient(10)
db = DataBaseService.get_service(DB_TEST)
table = 'test'

def prepare_database_1():
    columns = ['col1 %s primary key' % db.data_types['UUIDField'],
               'col2 %s' % db.data_types['BooleanField'],
               'col3 %s' % db.data_types['IntegerField'],
               'col4 %s' % db.data_types['SmallIntegerField'],
               'col5 %s' % db.data_types['FloatField'],
               'col6 %s' % db.data_types['TextField'],
               'col7 %s' % db.data_types['TimeField'],
               'col8 %s' % db.data_types['DateTimeField'],
               'col9 %s' % db.data_types['IPAddressField'],
               'col10 %s' % (db.data_types['CharField'] % {'max_length':20})]
    db.create_table(table, columns, lambda flag, result: flag)

def prepare_database_2():
    now = datetime.datetime.now()
    date_time = now.strftime('%Y-%m-%d %H:%M:%S')
    time_now = now.strftime('%H:%M:%S')
    rows = [['0', True, 1, 2, 1.23, 'abc', time_now, date_time, "127.0.0.1", "abc"],
            ['1', False, 3, 4, 3.14, 'def', time_now, date_time, "127.0.0.2", "def"],
            ['2', False, 3, 4, 3.14, 'def', time_now, date_time, "127.0.0.2", "def"]]
    for row in rows:
        db.insert(table, row, lambda flag, result: flag)

def reset_database():
    db.drop_table(table, lambda flag, result: flag)

def test_table_count():
    columns = ["DISTINCT", "col1"]
    db.count(table, columns, callback=lambda flag, result:test_callback(flag, result))

def test_callback(flag, result):
    print result
    test_table_count()

def start():
    print "Entering http request"
    request = HttpRequest("111.13.101.208", "GET", "/")
    client.http_request(request, 10, callback)

def callback(request, reply):
    time.sleep(1.0)
    print "Entering http callback"
    if reply != None:
        print request, reply
        print reply.body
    else:
        print "failed to fetch the request", str(request)

if __name__ == "__main__":
    # prepare_database_1()
    # time.sleep(0.1)
    # prepare_database_2()
    # time.sleep(0.1)
    # test_table_count()
    # reset_database()
    start()
    print '1111111111111111'
    # while True:
    #     Timer.loop(0.01, True, None, 1)
    #     print "-----------------------------------------------------"
