# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0046_mysalesorderreturnlineitem_credit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='description',
            field=models.CharField(default=b'', max_length=64, null=True, verbose_name='\u9644\u4ef6\u63cf\u8ff0', blank=True),
            preserve_default=True,
        ),
    ]
