# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0055_myreturnreason_result_item_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myreturnreason',
            name='result_item_type',
        ),
        migrations.AddField(
            model_name='myreturnreason',
            name='result_type',
            field=models.CharField(default=b'Refurbished', max_length=16, choices=[(b'New', b'New'), (b'Refurbished', b'Reburshied'), (b'Defect', b'Defect'), (b'Sample', b'Sample')]),
            preserve_default=True,
        ),
    ]
