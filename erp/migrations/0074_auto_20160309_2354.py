# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0073_auto_20160309_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyPOFullfillment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('reviewed_on', models.DateField(default=None, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='po_fullfillment_loggers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
                ('po', models.ForeignKey(to='erp.MyPurchaseOrder')),
                ('reviewed_by', models.ForeignKey(related_name='po_fullfillment_reviewers', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Reviewer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyPOFullfillmentLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fullfill_qty', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('po_fullfillment', models.ForeignKey(to='erp.MyPOFullfillment')),
                ('po_line_item', models.ForeignKey(to='erp.MyPurchaseOrderLineItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderfullfillment',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderfullfillment',
            name='po',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderfullfillment',
            name='reviewed_by',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderfullfillmentlineitem',
            name='po_fullfillment',
        ),
        migrations.DeleteModel(
            name='MyPurchaseOrderFullfillment',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderfullfillmentlineitem',
            name='po_line_item',
        ),
        migrations.DeleteModel(
            name='MyPurchaseOrderFullfillmentLineItem',
        ),
    ]
