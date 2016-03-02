# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0046_mysalesorderreturnlineitem_credit'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysalesorderreturn',
            name='reviewed_by',
            field=models.ForeignKey(related_name='reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mysalesorderreturn',
            name='reviewed_on',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysalesorderreturn',
            name='created_by',
            field=models.ForeignKey(related_name='loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237'),
            preserve_default=True,
        ),
    ]
