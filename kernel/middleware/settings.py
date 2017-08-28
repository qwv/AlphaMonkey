# -*- coding: utf-8 -*-
"""
 settings.py
 
 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 
"""

ALLOWED_HOSTS = []

# Database

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'alpha_monkey',
            'USER': 'root',
            'PASSWORD': 'bearing',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    },
    'test': {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'alpha_monkey_test',
            'USER': 'root',
            'PASSWORD': 'bearing',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    }
}
