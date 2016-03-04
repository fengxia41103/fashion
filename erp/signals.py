from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from erp.models import *

@receiver(pre_save, sender=MySizeChart)
def MySizeChart_pre_save_hanelder(sender, instance, **kwargs):
	instance.size = instance.size.upper()

@receiver(post_save, sender=MyItem)
def MyItem_post_save_handler(sender, instance, created, **kwargs):
	'''
	Create MyItemInventory upon creation of MyItem
	'''
	# Location and Storage
	location = MyLocation.objects.filter(crm = instance.brand)			
	if len(location): location = location[0]
	else: 
		# Get location
		location = MyLocation(crm=instance.brand)
		location.save()

	# Create a storage
	storage, created = MyStorage.objects.get_or_create(location=location,is_primary=True)
	
	# Create MyItemInventory			
	for size in instance.size_chart.size.split(','):
		MyItemInventory(
			item = instance,
			size = size,
			storage = storage
		).save()	

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
				created_by = instance.created_by,
				inv = inv_item, # item_inventory object
				out = False, # we are putting items back into inventory
				qty = return_line_item.return_qty,
				# object_id = instance.id, # save RETURN_LINE_ITEM reference
				# content_type = ContentType.objects.get_for_model(instance),
				content_object = return_line_item,
				reason = 'Sales order RETURN: %s' % return_line_item.reason.description
			).save()

@receiver(post_save, sender=MySalesOrderFullfillment)
def MySalesOrderFullfillment_post_save_handler(sender, instance, **kwargs):
	if instance.reviewed_on:
		for item in MySalesOrderFullfillmentLineItem.objects.filter(so_fullfillment=instance):
			MyItemInventoryTheoreticalAudit(
				created_by = instance.created_by,
				inv = item.so_line_item.item, # item_inventory object
				out = True, # we are withdrawing item from inventory
				qty = item.fullfill_qty,
				content_object = item,
				reason = 'Sales order FULLFILLMENT'
			).save()
