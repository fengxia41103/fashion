# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0068_myinvoice_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyInvoiceReceiveItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('price', models.FloatField(null=True, verbose_name='Invoice price', blank=True)),
                ('inv_item', models.ForeignKey(to='erp.MyItemInventory')),
                ('invoice', models.ForeignKey(to='erp.MyInvoice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderinvoiceitem',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='mypurchaseorderinvoiceitem',
            name='po_line_item',
        ),
        migrations.DeleteModel(
            name='MyPurchaseOrderInvoiceItem',
        ),
        migrations.RenameField(
            model_name='myinvoice',
            old_name='external_invoice_number',
            new_name='invoice_no',
        ),
        migrations.RemoveField(
            model_name='myinvoice',
            name='reviewed_by',
        ),
        migrations.RemoveField(
            model_name='myinvoice',
            name='reviewed_on',
        ),
    ]
