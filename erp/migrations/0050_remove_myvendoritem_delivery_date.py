# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0049_auto_20160229_1935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myvendoritem',
            name='delivery_date',
        ),
    ]
