# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0083_auto_20160402_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='file_base64',
            field=models.TextField(default=None, help_text='Based64 encoded file data', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='thumbnail_base64',
            field=models.TextField(default=None, help_text='Base64 encoded thumbnail data', null=True, blank=True),
            preserve_default=True,
        ),
    ]
