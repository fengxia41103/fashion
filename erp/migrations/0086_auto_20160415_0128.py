# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0085_attachment_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='thumbnail',
            field=models.FileField(help_text='Thumbnails', upload_to=b'%Y/%m/%d', null=True, verbose_name='Thumbnails', blank=True),
            preserve_default=True,
        ),
    ]
