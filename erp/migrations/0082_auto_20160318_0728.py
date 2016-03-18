# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0081_myshoppingcart_myshoppingcartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='myshoppingcart',
            name='is_open',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myshoppingcartitem',
            name='cart',
            field=models.ForeignKey(default=None, to='erp.MyShoppingCart'),
            preserve_default=False,
        ),
    ]
