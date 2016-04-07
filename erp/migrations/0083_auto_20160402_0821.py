# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0082_auto_20160318_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myinvoice',
            name='gross_cost',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
