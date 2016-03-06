# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0063_auto_20160305_2323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='abbrev',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='description',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='hash',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='help_text',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorder',
            name='name',
        ),
    ]
