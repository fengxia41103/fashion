# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0048_auto_20160228_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mylocation',
            name='name',
            field=models.CharField(max_length=32, verbose_name='\u540d\u79f0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myvendoritem',
            name='msrp',
            field=models.FloatField(blank=True, null=True, verbose_name='MSRP', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myvendoritem',
            name='price',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=True,
        ),
    ]
