# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0087_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyPOFulfillment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('reviewed_on', models.DateField(default=None, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='po_fulfillment_loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
                ('invoices', models.ManyToManyField(to='erp.MyInvoice')),
                ('po', models.ForeignKey(to='erp.MyPurchaseOrder')),
                ('reviewed_by', models.ForeignKey(related_name='po_fulfillment_reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Reviewer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyPOFulfillmentLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fulfill_qty', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('invoice', models.ForeignKey(to='erp.MyInvoice')),
                ('po_fulfillment', models.ForeignKey(to='erp.MyPOFulfillment')),
                ('po_line_item', models.ForeignKey(to='erp.MyPurchaseOrderLineItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySalesOrderFulfillment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('reviewed_on', models.DateField(default=None, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='so_fulfillment_loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
                ('reviewed_by', models.ForeignKey(related_name='so_fulfillment_reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Reviewer')),
                ('so', models.ForeignKey(to='erp.MySalesOrder')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySalesOrderFulfillmentLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fulfill_qty', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('so_fulfillment', models.ForeignKey(to='erp.MySalesOrderFulfillment')),
                ('so_line_item', models.ForeignKey(to='erp.MySalesOrderLineItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mypofullfillment',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='mypofullfillment',
            name='invoices',
        ),
        migrations.RemoveField(
            model_name='mypofullfillment',
            name='po',
        ),
        migrations.RemoveField(
            model_name='mypofullfillment',
            name='reviewed_by',
        ),
        migrations.RemoveField(
            model_name='mypofullfillmentlineitem',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='mypofullfillmentlineitem',
            name='po_fullfillment',
        ),
        migrations.DeleteModel(
            name='MyPOFullfillment',
        ),
        migrations.RemoveField(
            model_name='mypofullfillmentlineitem',
            name='po_line_item',
        ),
        migrations.DeleteModel(
            name='MyPOFullfillmentLineItem',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillment',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillment',
            name='reviewed_by',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillment',
            name='so',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillmentlineitem',
            name='so_fullfillment',
        ),
        migrations.DeleteModel(
            name='MySalesOrderFullfillment',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillmentlineitem',
            name='so_line_item',
        ),
        migrations.DeleteModel(
            name='MySalesOrderFullfillmentLineItem',
        ),
    ]
