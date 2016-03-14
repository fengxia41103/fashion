# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0078_auto_20160313_0106'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyInvoiceReceive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('reviewed_on', models.DateField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='invoice_receive_loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Invoice receive createed by')),
                ('invoice', models.ForeignKey(to='erp.MyInvoice')),
                ('reviewed_by', models.ForeignKey(related_name='invoice_receive_reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Invoice receive reviewed by')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyInvoiceReceiveItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('invoice_receive', models.ForeignKey(to='erp.MyInvoiceReceive')),
                ('item', models.ForeignKey(to='erp.MyInvoiceItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
