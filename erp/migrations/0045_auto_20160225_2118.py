# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0044_auto_20160225_2017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysalesorderreturnlineitem',
            old_name='so_fullfillment',
            new_name='so_return',
        ),
    ]
