# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0056_auto_20160301_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='myreturnreason',
            name='category',
            field=models.CharField(default='Service', max_length=16, choices=[(b'Small', b'Sizing too small'), (b'Large', b'Sizing too large'), (b'Quality', b'Quality/Satisfaction'), (b'Color', b'Color'), (b'Service', b'Service')]),
            preserve_default=False,
        ),
    ]
