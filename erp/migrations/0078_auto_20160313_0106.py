# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0077_mypofullfillmentlineitem_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyInvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('inv_item', models.ForeignKey(to='erp.MyItemInventory')),
                ('invoice', models.ForeignKey(to='erp.MyInvoice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='myinvoicereceiveitem',
            name='inv_item',
        ),
        migrations.RemoveField(
            model_name='myinvoicereceiveitem',
            name='invoice',
        ),
        migrations.DeleteModel(
            name='MyInvoiceReceiveItem',
        ),
    ]
