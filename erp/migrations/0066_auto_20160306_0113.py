# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0065_mypurchaseorderlineitem_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='mypurchaseorder',
            name='placed_on',
            field=models.DateField(null=True, verbose_name='Order placed on', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mypurchaseorder',
            name='so',
            field=models.ForeignKey(verbose_name='Associated sales order', blank=True, to='erp.MySalesOrder', null=True),
            preserve_default=True,
        ),
    ]
