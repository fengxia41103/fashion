# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0045_auto_20160225_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysalesorderreturnlineitem',
            name='credit',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
