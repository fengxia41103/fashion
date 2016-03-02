# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0058_myreturnreason_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myreturnreason',
            name='code',
            field=models.CharField(default=b'', unique=True, max_length=8),
            preserve_default=True,
        ),
    ]
