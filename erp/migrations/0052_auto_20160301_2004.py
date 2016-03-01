# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('erp', '0051_auto_20160301_1948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myiteminventorymoveaudit',
            name='so',
        ),
        migrations.AddField(
            model_name='myiteminventorymoveaudit',
            name='content_type',
            field=models.ForeignKey(default='', to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='myiteminventorymoveaudit',
            name='object_id',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
    ]
