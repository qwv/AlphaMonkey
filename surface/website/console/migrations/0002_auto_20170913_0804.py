# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-13 08:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectiontaskhistory',
            old_name='finish_time',
            new_name='end_time',
        ),
        migrations.RemoveField(
            model_name='collectiontask',
            name='finish_time',
        ),
    ]