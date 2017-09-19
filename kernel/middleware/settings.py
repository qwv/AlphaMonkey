# -*- coding: utf-8 -*-
"""
 settings.py
 
 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 
"""

ALLOWED_HOSTS = []

# Database

DB_DEFAULT = 'default'
DB_TEST = 'test'
DB_AMERICAN = 'american'

DATABASES = {
    DB_DEFAULT: {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'alpha_monkey',
            'USER': 'root',
            'PASSWORD': 'bearing',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    },
    DB_TEST: {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'alpha_monkey_test',
            'USER': 'root',
            'PASSWORD': 'bearing',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    },
    DB_AMERICAN: {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'finance_american',
            'USER': 'root',
            'PASSWORD': 'bearing',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    }
}
