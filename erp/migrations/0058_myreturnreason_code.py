# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0057_myreturnreason_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='myreturnreason',
            name='code',
            field=models.CharField(default=b'', max_length=8),
            preserve_default=True,
        ),
    ]
