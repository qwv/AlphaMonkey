# -*- coding: utf-8 -*-
"""
 log.py
 
 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 
"""

import sys, new
import logging 
import traceback
import logging.handlers as LH
import time
import json
import platform

def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    if tb == None:
        return
    while tb:
        tbinfo.append((
        tb.tb_frame.f_code.co_filename,
        tb.tb_frame.f_code.co_name,
        str(tb.tb_lineno)
        ))
        tb = tb.tb_next

    # just to be safe
    del tb

    pfile, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (pfile, function, line), t, v, info

def log_compact_traceback(self):
	self.error( traceback.format_exc() )
	
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARN
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG

STREAM 	= "stream"
SYSLOG 	= "syslog"
FILE	= "file"
	
class LogManager(object):
    created_modules = set()
    log_level = DEBUG
    log_handle = STREAM
    log_tag = ''
    sa_log_tag = ''
    sys_logger = None

    @staticmethod
    def get_logger (moduleName):
        # If we have it already, return it directly
        if LogManager.log_handle == SYSLOG and platform.system() == 'Linux' and LogManager.sys_logger != None:
            return logging.LoggerAdapter(LogManager.sys_logger, {'modulename': moduleName})

        if moduleName in LogManager.created_modules:
            return logging.getLogger(moduleName)
        logger = logging.getLogger(moduleName)
        logger.log_last_except = new.instancemethod(log_compact_traceback, logger, logger.__class__) 
        logger.setLevel(LogManager.log_level)  
        # create handler
        formatlist = ['%(asctime)s', 'AlphaMonkey', LogManager.log_tag, '%(name)s', '%(levelname)s', '%(message)s']
        if LogManager.log_handle == SYSLOG:
            if platform.system() == 'Linux':
                #debug logs use LOG_LOCAL1
                ch = LH.SysLogHandler(address='/dev/log', facility=LH.SysLogHandler.LOG_LOCAL1)
                LogManager.sys_logger = logger
                formatlist = ['%(asctime)s', 'AlphaMonkey', LogManager.log_tag, '%(modulename)s', '%(levelname)s', '%(message)s']
            else:
                ch = logging.FileHandler(LogManager.log_tag+ "_" + time.strftime("%Y%m%d_%H%M%S")+'.log', encoding='utf8')
        elif LogManager.log_handle == FILE:
            ch = logging.FileHandler(LogManager.log_tag+ "_" + time.strftime("%Y%m%d_%H%M%S")+'.log', encoding='utf8')
        else:
            ch = logging.StreamHandler()
        
        ch.setLevel(LogManager.log_level)  
        # create formatter and add it to the handlers
        formatter = logging.Formatter(' - '.join(formatlist))  
        ch.setFormatter(formatter)  
        # add the handlers to logger  
        logger.addHandler(ch)
        LogManager.created_modules.add(moduleName)

        if LogManager.log_handle == SYSLOG and platform.system() == 'Linux' and LogManager.sys_logger != None:
            return logging.LoggerAdapter(LogManager.sys_logger, {'modulename': moduleName})

        return logger
    
    @staticmethod
    def set_log_level (lv):
        LogManager.log_level = lv
    
    @staticmethod
    def set_log_handle(handle):
        LogManager.log_handle = handle
    
    @staticmethod
    def set_log_tag(log_tag):
        LogManager.log_tag = log_tag
