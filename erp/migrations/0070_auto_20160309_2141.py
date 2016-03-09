# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0069_auto_20160309_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='myinvoice',
            name='reviewed_by',
            field=models.ForeignKey(related_name='invoice_reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Invoice reviewed by'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myinvoice',
            name='reviewed_on',
            field=models.DateField(default=None, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='myinvoice',
            name='created_by',
            field=models.ForeignKey(related_name='invoice_loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Invoice createed by'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myinvoice',
            name='invoice_no',
            field=models.CharField(max_length=128, null=True, verbose_name='Invoice no.', blank=True),
            preserve_default=True,
        ),
    ]
