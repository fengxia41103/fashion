# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0062_auto_20160304_0611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mypurchaseorderlineitem',
            name='invoiced_qty',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderlineitem',
            name='packinglist_qty',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderlineitem',
            name='so_line_item',
        ),
        migrations.AddField(
            model_name='mylocation',
            name='is_primary',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mypurchaseorder',
            name='location',
            field=models.ForeignKey(default=None, to='erp.MyLocation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mypurchaseorderlineitem',
            name='inv_item',
            field=models.ForeignKey(default=None, to='erp.MyItemInventory'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mystorage',
            name='is_primary',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
