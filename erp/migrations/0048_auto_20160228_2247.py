# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0047_auto_20160228_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='myvendoritem',
            name='msrp',
            field=models.FloatField(null=True, verbose_name='MSRP', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myvendoritem',
            name='sku',
            field=models.CharField(default=b'', max_length=32, null=True, blank=True),
            preserve_default=True,
        ),
    ]
