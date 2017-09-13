# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class CollectionBuildinTask(models.Model):
    '''Django auto added id serial primary key.'''
    # id = models.BigAutoField(primary_key=True, unique=True)
    sign = models.IntegerField()
    action = models.CharField(max_length=32)
    content = models.TextField()

    class Meta:
        db_table = 'collection_buildin_task'


class CollectionSource(models.Model):
    type = models.CharField(max_length=32)
    url = models.URLField()
    url_field = models.CharField(max_length=128)
    data_format = models.CharField(max_length=32)
    time_interval = models.FloatField()

    class Meta:
        db_table = 'collection_source'


class CollectionTask(models.Model):
    sign = models.IntegerField()
    type = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    progress = models.CharField(max_length=32)
    begin_time = models.DateTimeField()

    class Meta:
        db_table = 'collection_task'


class CollectionTaskHistory(models.Model):
    sign = models.IntegerField()
    type = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    progress = models.CharField(max_length=32)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = 'collection_task_history'
