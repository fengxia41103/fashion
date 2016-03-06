# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0064_auto_20160305_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='mypurchaseorderlineitem',
            name='qty',
            field=models.PositiveIntegerField(default=1),
            preserve_default=True,
        ),
    ]
