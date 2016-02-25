# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erp', '0043_auto_20160223_2100'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyReturnReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True)),
                ('name', models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('abbrev', models.CharField(max_length=8, null=True, verbose_name='Abbreviation', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_refundable', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySalesOrderReturn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
                ('so', models.ForeignKey(to='erp.MySalesOrder')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySalesOrderReturnLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('return_qty', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('reason', models.ForeignKey(to='erp.MyReturnReason')),
                ('so_fullfillment', models.ForeignKey(to='erp.MySalesOrderReturn')),
                ('so_line_item', models.ForeignKey(to='erp.MySalesOrderLineItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillment',
            name='po',
        ),
        migrations.RemoveField(
            model_name='mysalesorderfullfillmentlineitem',
            name='po_line_item',
        ),
    ]
