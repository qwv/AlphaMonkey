# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *
# Register your models here.

class CollectionSourceAdmin(admin.ModelAdmin):
    list_display = ('type', 'url', 'url_field', 'data_format', 'time_interval')

class CollectionTaskAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'begin_time', 'progress')

class CollectionTaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'begin_time', 'end_time', 'progress')
    list_filter = ['begin_time', 'end_time']
    search_fields = ['type']

class CollectionBuildinTaskAdmin(admin.ModelAdmin):
    list_display = ('sign', 'action', 'content')

admin.site.register(CollectionSource, CollectionSourceAdmin)
admin.site.register(CollectionTask, CollectionTaskAdmin)
admin.site.register(CollectionTaskHistory, CollectionTaskHistoryAdmin)
admin.site.register(CollectionBuildinTask, CollectionBuildinTaskAdmin)
