import unittest
import sys
import datetime
import random
import time
import threading
import traceback

sys.path.append("..")

from middleware.db import DataBaseService
from middleware.settings import *
from middleware.log import *
from middleware.http import *
from middleware.thread import *
from middleware.timer import Timer


def prepare_database_1():
    db = DataBaseService.get_service(DB_TEST)
    table = 'test'
    columns = ['col1 %s primary key' % db.db_client.data_types['UUIDField'],
               'col2 %s' % db.db_client.data_types['BooleanField'],
               'col3 %s' % db.db_client.data_types['IntegerField'],
               'col4 %s' % db.db_client.data_types['SmallIntegerField'],
               'col5 %s' % db.db_client.data_types['FloatField'],
               'col6 %s' % db.db_client.data_types['TextField'],
               'col7 %s' % db.db_client.data_types['TimeField'],
               'col8 %s' % db.db_client.data_types['DateTimeField'],
               'col9 %s' % db.db_client.data_types['IPAddressField'],
               'col10 %s' % (db.db_client.data_types['CharField'] % {'max_length':20})]
    db.create_table(table, columns, lambda flag, result: flag)

def prepare_database_2():
    db = DataBaseService.get_service(DB_TEST)
    table = 'test'
    now = datetime.datetime.now()
    date_time = now.strftime('%Y-%m-%d %H:%M:%S')
    time = now.strftime('%H:%M:%S')
    rows = [['0', True,  1, 2, 1.23, 'abc', time, date_time, "127.0.0.1", "abc"],
            ['1', False, 3, 4, 3.14, 'def', time, date_time, "127.0.0.2", "def"]]
    for row in rows:
        db.insert(table, row, lambda flag, result: flag)

def reset_database():
    db = DataBaseService.get_service(DB_TEST)
    table = 'test'
    db.drop_table(table, lambda flag, result: flag)


class DBTests(unittest.TestCase):
    """
    Test DataBase Connection.
    """

    def setUp(self):
        print "-- Test database connection --"
        self.db = DataBaseService.get_service(DB_TEST)
        self.assertTrue(self.db.db_client.connected, "Connect db test failure.")
        self.table = 'test'

    def tearDown(self):
        time.sleep(0.1)

    def test_table_delete(self):
        condition = ["col1", self.db.db_client.operators['exact'] % 0]
        self.assertTrue(self.db.delete(self.table, condition, callback = lambda flag, result:self.assertTrue(flag)))
        self.assertTrue(self.db.delete(self.table, None, callback = lambda flag, result:self.assertTrue(flag)))

    def test_table_update(self):
        expressions = ["col6", self.db.db_client.operators['exact'] % "'ghi'"]
        condition = ["col3", self.db.db_client.operators['exact'] % 1]
        self.assertTrue(self.db.update(self.table, expressions, condition, callback = lambda flag, result:self.assertTrue(flag)))
        self.assertTrue(self.db.update(self.table, expressions, None, callback = lambda flag, result:self.assertTrue(flag)))

    def test_table_find(self):
        columns = ["col1", "col2"]
        condition = ["col1", self.db.db_client.operators['exact'] % 1]
        for _ in range(100):
            self.assertTrue(self.db.find(self.table, columns, condition, callback = lambda flag, result:self.assertTrue(flag)))

    def test_table_count(self):
        columns = ["DISTINCT", "col1"]
        self.assertTrue(self.db.count(self.table, columns, callback = lambda flag, result:self.assertTrue(flag)))
        self.assertTrue(self.db.count(self.table, "*", callback = lambda flag, result:self.assertTrue(flag)))


class LogTests(unittest.TestCase):
    """
    Test Log System.
    """

    def setUp(self):
        print "-- Test log system --"

    def test_stream_log(self):
        LogManager.set_log_handle(STREAM)
        logger = LogManager.get_logger("TestStreamLog")
        self.assertNotEqual(logger, None)
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warn message")
        logger.error("error message")
        logger.critical("critical message")

    def test_system_log(self):
        LogManager.set_log_handle(SYSLOG)
        logger = LogManager.get_logger("TestSysLog")
        self.assertNotEqual(logger, None)
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warn message")
        logger.error("error message")
        logger.critical("critical message")

    def test_file_log(self):
        LogManager.set_log_handle(FILE)
        logger = LogManager.get_logger("TestFileLog")
        self.assertNotEqual(logger, None)
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warn message")
        logger.error("error message")
        logger.critical("critical message")


class HttpTests(unittest.TestCase):
    """
    Test Http Request.
    """

    def setUp(self):
        print "-- Test http request --"
        self.client = AsyncHTTPClient(10)

    def callback(self, request, reply):
        print "Entering http callback"
        if reply != None:
            print request, reply
            print reply.body
        else:
            print "failed to fetch the request", str(request)

    def test_async_http_request(self):
        print "Entering http request"
        request = HttpRequest("111.13.101.208", "GET", "/")
        self.client.http_request(request, 10, self.callback)

    def test_async_https_request(self):
        print "Entering https request"
        request = HttpRequest("111.13.101.208", "GET", "/", usessl = True)
        self.client.http_request(request, 10, self.callback)


class ThreadPoolTests(unittest.TestCase):
    """
    Test Thread Pool.
    """

    def setUp(self):
        print "-- Test thread pool --"


class TimerTests(unittest.TestCase):
    """
    Test Timer.
    """

    def setUp(self):
        print "-- Test timer --"

    def tearDown(self):
        print "Wait 0.1s."
        time.sleep(0.1)

    def callback(self):
        print "Timer call back."

    def test_add_timer(self):
        print "Start a timer for 0.1 second."
        self.assertNotEqual(Timer.add_timer(0.1, self.callback), None)



class TimerThread(threading.Thread):
    
    def __init__(self, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self._dismissed = threading.Event()

    def run(self):
        while True:
            if self._dismissed.isSet():
                break
            try:
                Timer.loop(0.01)
            except KeyboardInterrupt:
                break
            except: #ignore all exceptions
                traceback.print_stack()
                pass
        Timer.close_all()
        print "Threading stop."

    def dismiss(self):
        self._dismissed.set()

thread = TimerThread()

class AAA_ThreadStartTests(unittest.TestCase):
    """
    Test Thread Start.
    """

    def test_thread_start(self):
        print "-- Test thread start --"
        thread.start()
        prepare_database_1()
        time.sleep(0.1)
        prepare_database_2()
        time.sleep(0.1)


class ZZZ_ThreadStopTests(unittest.TestCase):
    """
    Test Thread Stop.
    """

    def test_thread_stop(self):
        print "-- Test thread stop --"
        time.sleep(0.1)
        reset_database()
        time.sleep(0.5)
        thread.dismiss()
        # thread.join() #this will hang up main thread




#Test order by A-Z
if __name__ == "__main__":
    unittest.main()

