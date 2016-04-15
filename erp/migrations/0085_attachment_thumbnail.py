# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0084_auto_20160414_0411'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='thumbnail',
            field=models.FileField(default=None, help_text='Thumbnails', verbose_name='Thumbnails', upload_to=b'%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
