import unittest
import sys
import datetime
import random
import time

sys.path.append("..")

from middleware.db import DatabaseProxy
from middleware.settings import *
from middleware.log import *
from middleware.http import *
from middleware.thread import *

class DBTests(unittest.TestCase):
    """
    Test DBManager.
    """

    def setUp(self):
        print "-- Test db --"

        self.db = DatabaseProxy(DATABASES['test']['ENGINE'], DATABASES['test']['CONFIG'])
        self.assertTrue(self.db.db_client.connected, "Connect db test failure.")
        self.table = 'test'
        self.columns = ['col1 %s primary key' % self.db.db_client.data_types['UUIDField'],
                        'col2 %s' % self.db.db_client.data_types['BooleanField'],
                        'col3 %s' % self.db.db_client.data_types['IntegerField'],
                        'col4 %s' % self.db.db_client.data_types['SmallIntegerField'],
                        'col5 %s' % self.db.db_client.data_types['FloatField'],
                        'col6 %s' % self.db.db_client.data_types['TextField'],
                        'col7 %s' % self.db.db_client.data_types['TimeField'],
                        'col8 %s' % self.db.db_client.data_types['DateTimeField'],
                        'col9 %s' % self.db.db_client.data_types['IPAddressField']]
        now = datetime.datetime.now()
        date_time = now.strftime('%Y-%m-%d %H:%M:%S')
        time = now.strftime('%H:%M:%S')
        self.rows = [['0', True,  1, 2, 1.23, 'abc', time, date_time, "127.0.0.1"],
                     ['1', False, 3, 4, 3.14, 'def', time, date_time, "127.0.0.2"]]
        self.assertNotEqual(self.db.create_table(self.table, self.columns), None)
        for row in self.rows:
            self.assertNotEqual(self.db.insert(self.table, row), None)

    def test_table_drop(self):
        self.assertNotEqual(self.db.drop_table(self.table), None)

    def test_table_delete(self):
        condition = ["col1", self.db.db_client.operators['exact'] % 1]
        self.assertNotEqual(self.db.delete(self.table, condition), None)
        self.assertNotEqual(self.db.delete(self.table), None)
        self.test_table_drop()

    def test_table_update(self):
        expressions = ["col6", self.db.db_client.operators['exact'] % "'ghi'"]
        condition = ["col3", self.db.db_client.operators['exact'] % 1]
        self.assertNotEqual(self.db.update(self.table, expressions, condition), None)
        self.assertNotEqual(self.db.update(self.table, expressions), None)
        self.test_table_drop()

    def test_table_find(self):
        columns = ["col1", "col2"]
        condition = ["col1", self.db.db_client.operators['exact'] % 1]
        self.assertNotEqual(self.db.find(self.table, columns, condition), None)
        self.test_table_drop()

    def test_table_count(self):
        columns = ["DISTINCT", "col1"]
        self.assertNotEqual(self.db.count(self.table, columns), None)
        self.assertNotEqual(self.db.count(self.table), None)
        self.test_table_drop()


class LogTests(unittest.TestCase):
    """
    Test Log System.
    """

    def setUp(self):
        print "-- Test log --"

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
        print "-- Test http --"
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

    
class ThreadTests(unittest.TestCase):
    """
    Test Thread Pool.
    """

    def setUp(self):
        print "-- Test thread --"




if __name__ == "__main__":
    unittest.main()
