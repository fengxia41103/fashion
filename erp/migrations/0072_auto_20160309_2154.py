# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0071_remove_myinvoicereceiveitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myinvoice',
            name='reviewed_on',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
