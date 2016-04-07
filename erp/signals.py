from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from tastypie.models import create_api_key

from datetime import datetime as dt
from erp.models import *

###################################################
#
#	MySizeChart signals
#
###################################################	
@receiver(pre_save, sender=MySizeChart)
def MySizeChart_pre_save_hanelder(sender, instance, **kwargs):
	instance.size = instance.size.upper()

###################################################
#
#	Item signals
#
###################################################	
@receiver(pre_save, sender=MyItem)
def MyItem_pre_save_handler(sender, instance, **kwargs):
	try:
		obj = sender.objects.get(pk=instance.pk)
	except sender.DoesNotExist:
		pass # Object is new, so field hasn't technically changed, but you may want to do something else here.
	else:
		if not obj.size_chart == instance.size_chart: # Field has changed
			old_chart = obj.size_chart.size.split(',')
			new_chart = instance.size_chart.size.split(',')

			# We are swapping size chart, eg SML -> 2,4,6
			# Size chart should always be 5 levels!
			if len(old_chart) == len(new_chart):
				for (old_size,new_size) in zip(old_chart,new_chart):
					for item_inv in MyItemInventory.objects.filter(item=instance,size=old_size):
						item_inv.size = new_size
						item_inv.save()
			elif not obj.size_chart: # is None, creating ItemInventory
				# Location and Storage
				location = MyLocation.objects.filter(crm = instance.brand)			
				if len(location): location = location[0]
				else: 
					# Get location
					location = MyLocation(
						name = instance.brand.name,
						crm = instance.brand
					)
					location.save()

				# Create a storage
				storage, created = MyStorage.objects.get_or_create(location=location,is_primary=True)
				
				# Create MyItemInventory			
				for new_size in new_chart:
					MyItemInventory(
						item = instance,
						size = new_size,
						storage = storage
					).save()

###################################################
#
#	Sales order signals
#
###################################################	
@receiver(pre_save, sender=MyBusinessModel)
def MyBusinessModel_pre_save_handler(sender, instance, **kwargs):
	instance.name = instance.name.upper()	

@receiver(post_save, sender=MySalesOrder)
def MySalesOrder_post_save_handler(sender,instance,**kwargs):
	# Type 1: SO -> fullfillment -> payment -> done
	# Scenario: retail, wholesale
	# All payments would be cleared immediately at sales.
	# In this type, we auto created a SO Fullfillment and line items that mirrors SO and its line items,
	# and auto-populate fullfilled qty!
	if instance.business_model.process_model == 1:
		so_fullfillment,created = MySalesOrderFullfillment.objects.get_or_create(
			so = instance,
			created_by = instance.created_by
		)

@receiver(post_save, sender=MySalesOrderLineItem)
def MySalesOrderLineItem_post_save_handler(sender,instance,**kwargs):
	if instance.order.business_model.process_model == 1:
		'''
		For retail order, auto create SO fullfillment from SO creation.
		'''
		so_fullfillment, created = MySalesOrderFullfillment.objects.get_or_create(
			so = instance.order,
			created_by = instance.order.created_by
		)
		so_line_item,created = MySalesOrderFullfillmentLineItem.objects.get_or_create(
			so_fullfillment = so_fullfillment,
			so_line_item = instance,
			fullfill_qty = instance.qty
		)

@receiver(pre_save, sender=MySalesOrderReturnLineItem)
def MySalesOrderReturnLineItem_pre_save_handler(sender,instance,**kwargs):
	if instance.reason.is_refundable:
		instance.credit = instance.so_line_item.price*instance.return_qty

@receiver(post_save, sender=MySalesOrderReturn)
def MySalesOrderReturn_post_save_handler(sender, instance, **kwargs):
	if instance.reviewed_on:
		for return_line_item in MySalesOrderReturnLineItem.objects.filter(so_return=instance):
			old_inv_item = return_line_item.so_line_item.item
			inv_item, created = MyItemInventory.objects.get_or_create(
				item = old_inv_item.item,
				size = old_inv_item.size,
				storage = old_inv_item.storage,
				item_type = return_line_item.reason.result_type
			)
			
			MyItemInventoryTheoreticalAudit(
				created_by = instance.reviewed_by,
				inv = inv_item, # item_inventory object
				out = False, # we are putting items back into inventory
				qty = return_line_item.return_qty,
				content_object = return_line_item,
				reason = 'Sales order RETURN: %s' % return_line_item.reason.description
			).save()

@receiver(post_save, sender=MySalesOrderFullfillment)
def MySalesOrderFullfillment_post_save_handler(sender, instance, **kwargs):
	if instance.reviewed_on:
		for item in MySalesOrderFullfillmentLineItem.objects.filter(so_fullfillment=instance):
			MyItemInventoryTheoreticalAudit(
				created_by = instance.reviewed_by,
				inv = item.so_line_item.item, # item_inventory object
				out = True, # we are withdrawing item from inventory
				qty = item.fullfill_qty,
				content_object = item,
				reason = 'Sales order FULLFILLMENT'
			).save()

@receiver(post_save, sender=MySalesOrderPayment)
def MySalesOrderPayment_post_save_handler(sender,instance,**kwargs):
	if instance.reviewed_on:
		# Type 2: SO -> downpayment -> PO -> PO invoice -> PO fullfillment -> SO fullfillment -> payment -> done
		# Scenario: proxy
		# Order is active when there is a reviewed "deposit" payment. System will
		# auto create PO back-to-back to SO.
		so = instance.so
		if so.business_model.process_model == 2 and so.is_po_needed and instance.usage=='deposit':
			# create POs
			po_list = {}	
			for vendor in instance.so.vendors:
				po = MyPurchaseOrder(
					so = so,
					vendor = vendor,
					location = so.default_storage.location,
					created_by = instance.reviewed_by,
				)
				po.save()
				po_list[vendor] = po

			for so_line_item in MySalesOrderLineItem.objects.filter(order=so):
				inv_item = so_line_item.item
				item = inv_item.item
				po = po_list[item.brand]
				MyPurchaseOrderLineItem(
					po = po,
					inv_item = inv_item,
					qty = so_line_item.qty
				).save()

###################################################
#
#	Invoice signals
#
###################################################	
@receiver(post_save, sender=MyInvoice)
def MyInvoice_post_save_handler(sender, instance, **kwargs):
	if instance.reviewed_on:
		rcv_items = MyInvoiceItem.objects.filter(invoice=instance)

		new_inventory = {}		
		for rcv_item in rcv_items:
			new_inventory[rcv_item.inv_item] = rcv_item.qty

		# Auto fullfill open PO items, sorted by order's created_on date stamp
		inv_items = set([rcv_item.inv_item for rcv_item in rcv_items])
		po_line_items = MyPurchaseOrderLineItem.objects.filter(inv_item__in=inv_items).order_by('po__created_on')

		if len(po_line_items): # has an associated PO
			group_by_po = {}
			for tmp in po_line_items:
				if tmp.po not in group_by_po: group_by_po[tmp.po] = []
				group_by_po[tmp.po].append(tmp)
			for po,line_items in group_by_po.iteritems():
				# create PO FULLFILLMENT
				fullfill = MyPOFullfillment(
					po = po,
					created_by = instance.reviewed_by,
				)
				fullfill.save()

				# add a reference to invoice
				fullfill.invoices.add(instance)

				# create line items
				for item in line_items:
					MyPOFullfillmentLineItem(
						po_fullfillment = fullfill,
						po_line_item = item,
						fullfill_qty = new_inventory[item.inv_item],
						invoice = instance
					).save()

				# auto finalize fullfill
				fullfill.reviewed_by = instance.reviewed_by
				fullfill.reviewed_on = dt.now()
				fullfill.save()
		else: # has no PO, we need to update inventory theoretical now
			for invoice_item in rcv_items:
				MyItemInventoryTheoreticalAudit(
					created_by = instance.reviewed_by,
					inv = invoice_item.inv_item,
					out = False,
					qty = invoice_item.qty,
					content_object = instance,
					reason = 'Sample INVOICE %s'% instance
				).save()

@receiver(post_save, sender=MyInvoiceItem)
def MyInvoiceItem_post_save_handler(sender, instance, **kwargs):
	if instance.qty < 1:
		'''
		Set line item qty to 0 = removing this line item from Invoice
		'''
		invoice = MyInvoice.objects.get(id=instance.invoice.id)

		# delete line item
		instance.delete()

		# delete invoice instance if there is not valid line items anymore!
		if invoice.total_qty < 1: invoice.delete()

###################################################
#
#	Purchase order signals
#
###################################################	
@receiver(post_save, sender=MyPOFullfillment)
def MyPOFullfillment_post_save_handler(sender, instance, **kwargs):
	if instance.reviewed_on:
		for fullfill_line_item in MyPOFullfillmentLineItem.objects.filter(po_fullfillment = instance):
			MyItemInventoryTheoreticalAudit(
				created_by = instance.reviewed_by,
				inv = fullfill_line_item.po_line_item.inv_item,
				out = False,
				qty = fullfill_line_item.fullfill_qty,
				content_object = instance,
				reason = 'Purchase order FULLFILLMENT from INVOICE %s'%fullfill_line_item.invoice
			).save()

		# from POFullfillment -> PO -> related SO -> created SO fullfillment
		so = instance.po.so
		if so and so.business_model.process_model == 2: # Proxy SO
			# create SOFullfillment
			so_fullfill = MySalesOrderFullfillment(
				so = so,
				created_by = instance.reviewed_by,
			)
			so_fullfill.save()

			# create SO fullfill line items
			for fullfill_line_item in MyPOFullfillmentLineItem.objects.filter(po_fullfillment = instance):
				po_line_item = fullfill_line_item.po_line_item
				inv_item = po_line_item.inv_item		
				so_line_item = MySalesOrderLineItem.objects.get(order=so,item=inv_item)

				# create so fullfillment line item
				qty = min(so_line_item.qty,fullfill_line_item.fullfill_qty)
				MySalesOrderFullfillmentLineItem(
					so_fullfillment = so_fullfill,
					so_line_item = so_line_item,
					fullfill_qty = qty
				).save()

###################################################
#
#	Inventory signals
#
###################################################	
@receiver(pre_save, sender=MyItemInventoryPhysicalAudit)
def MyItemInventoryPhysicalAudit_post_save_handler(sender, instance, **kwargs):
	# Saving a physical audit would also update ItemInventory's physical record
	instance.inv.physical = instance.physical
	instance.inv.save()

###################################################
#
#	User signals
#
###################################################
@receiver(post_save, sender=User)
def User_post_save_handler(sender, instance, **kwargs):
	create_api_key(sender,instance,**kwargs)
