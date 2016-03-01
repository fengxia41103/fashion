# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0053_myiteminventory_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='myiteminventory',
            name='item_type',
            field=models.CharField(default=b'New', max_length=16, choices=[(b'New', b'New'), (b'Refurbished', b'Reburshied'), (b'Defect', b'Defect'), (b'Sample', b'Sample')]),
            preserve_default=True,
        ),
    ]
