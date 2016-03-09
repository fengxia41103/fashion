# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0066_auto_20160306_0113'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('reviewed_on', models.DateField(null=True, blank=True)),
                ('external_invoice_number', models.CharField(max_length=128, null=True, verbose_name='External invoice number', blank=True)),
                ('issued_on', models.DateField()),
                ('gross_cost', models.FloatField()),
                ('discount', models.FloatField(default=0)),
                ('maturity_date', models.DateField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='Loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
                ('crm', models.ForeignKey(to='erp.MyCRM')),
                ('reviewed_by', models.ForeignKey(related_name='Reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Reviewer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyPurchaseOrderInvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('price', models.FloatField(null=True, verbose_name='Invoice price', blank=True)),
                ('invoice', models.ForeignKey(to='erp.MyInvoice')),
                ('po_line_item', models.ForeignKey(to='erp.MyPurchaseOrderLineItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
