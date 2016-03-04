# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('erp', '0061_auto_20160302_2309'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyItemInventoryPhysicalAudit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('physical', models.PositiveIntegerField(default=0)),
                ('theoretical', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Auditor')),
                ('inv', models.ForeignKey(to='erp.MyItemInventory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyItemInventoryTheoreticalAudit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('out', models.BooleanField(default=False)),
                ('qty', models.IntegerField(default=0)),
                ('object_id', models.PositiveIntegerField()),
                ('reason', models.TextField(default=b'')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='Auditor')),
                ('inv', models.ForeignKey(to='erp.MyItemInventory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='myiteminventorymoveaudit',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='myiteminventorymoveaudit',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='myiteminventorymoveaudit',
            name='inv',
        ),
        migrations.DeleteModel(
            name='MyItemInventoryMoveAudit',
        ),
        migrations.AlterField(
            model_name='myiteminventory',
            name='physical',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mypurchaseorder',
            name='so',
            field=models.ForeignKey(verbose_name='Sales order', blank=True, to='erp.MySalesOrder', null=True),
            preserve_default=True,
        ),
    ]
