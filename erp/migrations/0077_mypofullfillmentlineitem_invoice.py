# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0076_mypofullfillment_invoices'),
    ]

    operations = [
        migrations.AddField(
            model_name='mypofullfillmentlineitem',
            name='invoice',
            field=models.ForeignKey(default=None, to='erp.MyInvoice'),
            preserve_default=False,
        ),
    ]
