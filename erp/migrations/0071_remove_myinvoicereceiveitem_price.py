# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0070_auto_20160309_2141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myinvoicereceiveitem',
            name='price',
        ),
    ]
