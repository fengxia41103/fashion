# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0075_remove_myinvoice_enable_auto_fullfill'),
    ]

    operations = [
        migrations.AddField(
            model_name='mypofullfillment',
            name='invoices',
            field=models.ManyToManyField(to='erp.MyInvoice'),
            preserve_default=True,
        ),
    ]
