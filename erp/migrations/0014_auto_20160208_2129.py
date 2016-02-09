# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0013_myitem_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myitem',
            name='color',
            field=models.CharField(default=b'', max_length=128),
            preserve_default=True,
        ),
    ]
