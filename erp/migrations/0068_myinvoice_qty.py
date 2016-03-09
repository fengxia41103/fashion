# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0067_myinvoice_mypurchaseorderinvoiceitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='myinvoice',
            name='qty',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
