# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0050_remove_myvendoritem_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myiteminventorymoveaudit',
            name='so',
            field=models.ForeignKey(blank=True, to='erp.MySalesOrder', null=True),
            preserve_default=True,
        ),
    ]
