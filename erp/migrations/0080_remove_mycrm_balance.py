# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0079_myinvoicereceive_myinvoicereceiveitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mycrm',
            name='balance',
        ),
    ]
