# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from annoying.fields import JSONField # django-annoying
from django.db.models import Q
from datetime import datetime as dt
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from localflavor.us.forms import USPhoneNumberField


class MyBaseModel (models.Model):
	# fields
	hash = models.CharField (
		max_length = 256, # we don't expect using a hash more than 256-bit long!
		null = True,
		blank = True,
		default = '',
		verbose_name = u'MD5 hash'
	)
		
	# basic value fields
	name = models.CharField(
		default = None,
		max_length = 128,
		verbose_name = u'名称'
	)
	description = models.TextField (
		null=True, 
		blank=True,
		verbose_name = u'描述'
	)
	abbrev = models.CharField(
		max_length = 8,
		null = True,
		blank = True,
		verbose_name = u'Abbreviation'
	)
	
	# help text
	help_text = models.CharField (
		max_length = 64,
		null = True,
		blank = True,
		verbose_name = u'帮助提示'
	)

	# attachments
	attachments = GenericRelation('Attachment')
	notes = GenericRelation('MyNote')

	# is object active
	is_active = models.BooleanField(default = True)

	# this is an Abstract model
	class Meta:
		abstract=True

	def __unicode__(self):
		return self.name

######################################################
#
#	Tags
#
#####################################################
class MyTaggedItem (models.Model):
	# basic value fields
	tag = models.SlugField(
			default = '',
			max_length = 16,
			verbose_name = u'Tag'
	)	
	def __unicode__(self):
		return self.tag

######################################################
#
#	Attachments
#
#####################################################
class Attachment (models.Model):
	# generic foreign key to base model
	# so we can link attachment to any model defined below
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	# instance fields
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = ''
	)
		
	# basic value fields
	name = models.CharField(
		default = 'default name',
		max_length = 64,
		verbose_name = u'附件名称'
	)
	description = models.CharField (
		max_length = 64,
		default = 'default description',
		verbose_name = u'附件描述'
	)
	file = models.FileField (
		upload_to = '%Y/%m/%d',
		verbose_name = u'附件',
		help_text = u'附件'
	)	

	def __unicode__(self):
		return self.file.name

######################################################
#
#	Notes
#
#####################################################
class MyNote(models.Model):
	# generic foreign key to base model
	# so we can link attachment to any model defined below
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	content = models.TextField(
		verbose_name = u'Note'
	)

######################################################
#
#	App specific models
#
#####################################################
class MyCountry(models.Model):
	name = models.CharField(
		max_length = 64,
		verbose_name = u'Country name'
	)
	abbrev = models.CharField(
		max_length = 16,
		verbose_name = u'Country abbrev'
	)
	def __unicode__(self):
		return self.name

class MyCurrency(models.Model):
	name = models.CharField(
		max_length = 16,
		verbose_name = u'Currency name'
	)
	abbrev = models.CharField(
		max_length = 8,
		verbose_name = u'Currency abbrev'
	)
	symbol = models.CharField(
		max_length = 8,
		verbose_name = u'Currency symbol'
	)
	country = models.ForeignKey(
		'MyCountry'
	)
	def __unicode__(self):
		return self.symbol

class MyExchangeRate(models.Model):
	home = models.ForeignKey('MyCurrency', related_name = 'home_currency')
	foreign = models.ForeignKey('MyCurrency', related_name = 'foreign_currency')
	rate = models.FloatField(
		default = 1.0,
		verbose_name = u'Exchange rate'
	)

	def __unicode__(self):
		return u'%s = %s * %s' % (self.home,str(self.rate),self.foreign)

class MyUOM(models.Model):
	uom = models.CharField(
		max_length = 8,
		verbose_name = u'unit of measure'
	)
	description = models.TextField(
		null = True,
		blank = True,
	)

	def __unicode__(self):
		return self.uom

class MyFiscalYear(models.Model):
	begin = models.DateField(
		verbose_name = u'Fiscial year start'
	)
	end = models.DateField(
		verbose_name = u'Fiscal year end'
	)
	is_active = models.BooleanField(
		default = False,
	)

	def __unicode__(self):
		return '%s - %s'%(self.begin,self.end)

class MyCompany(MyBaseModel):
	home_currency = models.ForeignKey('MyCurrency')
	fiscal_year = models.ForeignKey('MyFiscalYear')

	phone = models.CharField(
		max_length = 16,
		null = True,
		blank = True,
		verbose_name = u'Company phone'
	)	

class MyLocation (models.Model):
	crm = models.ForeignKey('MyCRM')	
	name = models.CharField(
		default = None,
		max_length = 32,
		verbose_name = u'名称'
	)	
	address = models.TextField(default='')
	users = models.ManyToManyField(User,null=True,blank=True)
	abbrev = models.CharField(
		max_length = 5,
		null = True,
		blank = True,
	)

	def _code(self):
		return u'%s-%s' %(self.crm,self.name)
	code = property(_code)

	def __unicode__(self):
		return self.code

class MyStorage (models.Model):
	location = models.ForeignKey('MyLocation')
	is_primary = models.BooleanField(default=True)

	def _code(self):
		return u'%s-%d (%s)' %(self.location,self.id, self.location.abbrev)
	code = property(_code)

	def _physical(self):
		qty = [inv_item.physical for inv_item in MyItemInventory.objects.filter(storage=self)]
		return sum(qty)
	physical = property(_physical)

	def _theoretical(self):
		qty = [inv_item.theoretical for inv_item in MyItemInventory.objects.filter(storage=self)]
		return sum(qty)
	theoretical = property(_theoretical)

	def __unicode__(self):
		return self.code

class MyCRMCustomManager(models.Manager):
	def vendors(self):
		return self.get_queryset().filter(Q(crm_type='V')|Q(crm_type='B'))

	def customers(self):
		return self.get_queryset().filter(Q(crm_type='C')|Q(crm_type='B'))

class MyCRM(MyBaseModel):
	# custom managers
	# Note: the 1st one defined will be taken as the default!
	objects = MyCRMCustomManager()

	CRM_TYPE_CHOICES = (
		('B','Both'), # can only be WH internals
		('V','Vendor'), # can only  link to PO
		('C','Customer') # can only link to SO
	)
	crm_type = models.CharField(
		max_length = 16,
		default = 'vendor',
		choices = CRM_TYPE_CHOICES
	)
	contact = models.CharField(
		max_length = 32,
		null = True,
		blank = True,
		verbose_name = u'CRM contact'
	)	
	phone = models.CharField(
		max_length = 16,
		null = True,
		blank = True,
		verbose_name = u'Vendor phone'
	)
	url = models.URLField(
		null = True,
		blank = True,
		default='',
	)
	balance = models.FloatField(default = 0)
	currency = models.ForeignKey('MyCurrency')
	std_discount = models.FloatField(
		default=0.25,
		validators=[MaxValueValidator(1.0),MinValueValidator(0.0)]
	)

	def __unicode__(self):
		return self.name

	def _code(self):
		return '%04d' % self.id
	code = property(_code)
	
class MyVendorItem(models.Model):
	vendor = models.ForeignKey('MyCRM')

	# This is vendor SKU
	sku = models.CharField(
		max_length = 32,
		default = '',
	)
	price = models.FloatField(default = 0)
	currency = models.ForeignKey('MyCurrency')
	product = models.ForeignKey('MyItem')

	# If we know when is the deadline to place SO
	# against this item. This is observed when showing items
	# available for SO on e-Commerce site.
	order_deadline = models.DateField(
		null = True,
		blank = True,
	)

	# Default delivery date. This is a promise that vendor give
	# regarding this item. However, it can change per order basis.
	delivery_date = models.DateField(
		null = True,
		blank = True
	)

	# Minimal qty per line item
	minimal_qty = models.IntegerField(default = 1)	

class MySeason(models.Model):
	name = models.CharField(
		max_length = 8
	)
	def __unicode__(self):
		return self.name

	def _brands(self):
		brand_ids = set(MyItem.objects.filter(season=self).values_list('brand',flat=True))
		return MyCRM.objects.filter(id__in = brand_ids)
	brands = property(_brands)

class MySizeChart(models.Model):
	# CSV format, eg "S,M,L", "0,2,4,6","XS,S,M,L,XL"
	size = models.CharField(
		max_length = 128
	)
	def __unicode__(self):
		return self.size

class MyItem(MyBaseModel):
	'''
	Attachment would be item photos.
	'''
	season = models.ForeignKey('MySeason')
	brand = models.ForeignKey('MyCRM', verbose_name=u'品牌')
	color = models.CharField(
		max_length = 128,
		default = '',
	)
	price = models.FloatField(
		default = 0,
		validators=[MinValueValidator(0.0),]
	) # retail price
	currency = models.ForeignKey('MyCurrency')

	# size chart
	size_chart = models.ForeignKey(
		'MySizeChart',
		null = True,
		blank = True
	)

	def _code(self):
		return u'%s-%s' %(self.name,self.color)
	code = property(_code)

	def _product_id(self):
		return '#%06d' % self.id
	product_id = property(_product_id)

	def _available_left_in_days():
		if self.order_deadline: return (dt.now()-self.order_deadline).days
		else: return '-'
	available_left_in_days = property(_available_left_in_days)

	def _converted_cost(self):
		vendor_item = MyVendorItem.objects.filter(product=self,vendor=self.brand)[0]
		exchange_rate = None
		converted_cost = 0
		try:
			exchange_rate = MyExchangeRate.objects.get(home=self.currency, foreign=vendor_item.currency)
			converted_cost = vendor_item.price / exchange_rate.rate
		except: pass

		if not exchange_rate:
			try:
				exchange_rate = MyExchangeRate.objects.get(foreign=self.currency, home=vendor_item.currency)
				converted_cost = vendor_item.price * exchange_rate.rate
			except: pass
		return converted_cost		
	converted_cost = property(_converted_cost)

	def _multiplier(self):
		if self.converted_cost: return self.price / self.converted_cost
		else: return None
	multiplier = property(_multiplier)

	def _total_physical(self):
		return sum([qty for size,qty in self.physical])
	total_physical = property(_total_physical)

	def _total_theoretical(self):
		return sum([qty for size,qty in self.theoretical])
	total_theoretical = property(_total_theoretical)

	def _physical(self):
		qty = []
		for inv_item in MyItemInventory.objects.filter(item = self):
			if inv_item.withdrawable: qty.append((inv_item.size,inv_item.physical))
		return qty
	physical = property(_physical)

	def _theoretical(self):
		qty = []
		for inv_item in MyItemInventory.objects.filter(item = self).order_by('size'):
			qty.append((inv_item.size,inv_item.theoretical))
		return qty
	theoretical = property(_theoretical)

	def __unicode__(self):
		return u'%s | %s' %(self.name,self.color)

class MyItemInventory(models.Model):
	item = models.ForeignKey('MyItem')
	size = models.CharField(
		max_length = 4,
		default = ''
	)
	storage = models.ForeignKey('MyStorage')
	withdrawable = models.BooleanField(default = True)

	physical = models.IntegerField(
		default = 0,
		validators=[MinValueValidator(0),]
	)

	def _theoretical(self):
		inv = 0
		for audit in MyItemInventoryMoveAudit.objects.filter(inv = self):
			if audit.out: inv -= audit.qty
			else: inv += audit.qty
		return inv
	theoretical = property(_theoretical)

	def _code(self):
		return 'INV-%06d'%self.id
	code = property(_code)

class MyItemInventoryMoveAudit(models.Model):
	created_on = models.DateField(auto_now_add = True)

	# instance fields
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = ''
	)

	# Against this inventory we are adjusting
	inv = models.ForeignKey('MyItemInventory')

	# If True, we are depleting qty.
	out = models.BooleanField(default = False)
	qty = models.IntegerField(default = 0)

	# Linked PO or SO
	so = models.ForeignKey(
		'MySalesOrderFullfillment',
		null = True,
		blank = True,
	)
	reason = models.TextField(default='')

class MyBusinessModel(MyBaseModel):
	'''
	Define sales model that business supports.
	'''
	SALES_MODEL_CHOICES = (
		('Retail',u'零售'),
		('Wholesale',u'批发'),
		('Consignment',u'代销'),
		('Leasing',u'租赁'),
		('Proxy',u'订货'),
	)
	sales_model = models.CharField(
		max_length = 64,
		default = 'Retail',
		choices = SALES_MODEL_CHOICES
	)

	def __unicode__(self):
		return self.sales_model

	def _process_model(self):
		if self.sales_model in ['Retail','Wholesale']: return 1
		elif self.sales_model in ['Proxy']: return 2
		elif self.sales_model in ['Consignment']: return 3
		elif self.sales_model in ['Leasing']: return 4		
	process_model = property(_process_model)

class MySalesOrder(models.Model):
	business_model = models.ForeignKey('MyBusinessModel')
	customer = models.ForeignKey('MyCRM')
	sales = models.ForeignKey(User, related_name='sales')
	default_storage = models.ForeignKey('MyStorage',null=True,blank=True)
	created_on = models.DateField(auto_now_add = True)

	# instance fields
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = '',
		related_name='logger'
	)
	discount = models.FloatField(
		validators=[MaxValueValidator(1.0),MinValueValidator(0.0),]
	)

	# Set this flag to True for internal customers.
	# This will force line item price to use item's converted cost instead of RP.
	is_sold_at_cost = models.BooleanField(default=False)

	def __unicode__(self):
		return u'%s for %s'%(self.code,self.customer)

	def _code(self):
		return '%s%d-%04d'%(self.default_storage.location.abbrev,dt.now().year,self.id)
	code = property(_code)

	def _is_editable(self):
		'''
		Sales order becomes locked when there has been fullfillment or a payment
		'''
		return self.fullfill_qty == 0 and self.total_payment == 0
	is_editable = property(_is_editable)

	def _life_in_days(self):
		return (dt.now()-self.created_on).days
	life_in_days = property(_life_in_days)

	def _line_item_qty(self):
		return len(MySalesOrderLineItem.objects.filter(order=self).values_list('id',flat=True))
	line_item_qty = property(_line_item_qty)

	def _total_qty(self):
		return sum(MySalesOrderLineItem.objects.filter(order=self).values_list('qty',flat=True))
	total_qty = property(_total_qty)

	def _total_std_value(self):
		return sum([line.std_value for line in MySalesOrderLineItem.objects.filter(order=self)])
	total_std_value = property(_total_std_value)

	def _total_discount_value(self):
		return sum([line.discount_value for line in MySalesOrderLineItem.objects.filter(order=self)])
	total_discount_value = property(_total_discount_value)

	def _implied_discount(self):
		if self.total_std_value: return 1-self.total_discount_value/self.total_std_value
		else: return ''
	implied_discount = property(_implied_discount)

	def _fullfill_qty(self):
		return sum([line.fullfill_qty for line in MySalesOrderLineItem.objects.filter(order=self)])
	fullfill_qty = property(_fullfill_qty)

	def _fullfill_std_value(self):
		return sum([line.fullfill_qty*line.price for line in MySalesOrderLineItem.objects.filter(order=self)])
	fullfill_std_value = property(_fullfill_std_value)

	def _fullfill_discount_value(self):
		return sum([line.fullfill_qty*line.discount_price for line in MySalesOrderLineItem.objects.filter(order=self)])
	fullfill_discount_value = property(_fullfill_discount_value)

	def _fullfill_rate_by_qty(self):
		if self.total_qty: return self.fullfill_qty*100.0/self.total_qty
		else: return ''
	fullfill_rate_by_qty = property(_fullfill_rate_by_qty)

	def _fullfill_rate_by_value(self):
		if self.total_std_value: return self.fullfill_std_value*100.0/ self.total_std_value
		else: return ''
	fullfill_rate_by_value = property(_fullfill_rate_by_value)

	def _last_fullfill_date(self):
		try:
			return MySalesOrderFullfillment.objects.filter(so=self).order_by('-created_on')[0].created_on
		except: return ''
	last_fullfill_date = property(_last_fullfill_date)

	def _fullfillments(self):
		return MySalesOrderFullfillment.objects.filter(so=self).order_by('-created_on')
	fullfillments = property(_fullfillments)

	def _discount_in_pcnt(self):
		return '%d%%' % (self.discount*100)
	discount_in_pcnt = property(_discount_in_pcnt)

	def _payments(self):
		return MySalesOrderPayment.objects.filter(so=self)
	payments = property(_payments)

	def _total_payment(self):
		return sum([p.amount for p in MySalesOrderPayment.objects.filter(so=self)])
	total_payment = property(_total_payment)

	def _account_receivable(self):
		'''
		AR is computed by actual fullfilled value instead of what's on order.
		'''
		return self.fullfill_discount_value - self.total_payment
	account_receivable = property(_account_receivable)

class MySalesOrderLineItem(models.Model):
	order = models.ForeignKey('MySalesOrder')
	item = models.ForeignKey('MyItemInventory')
	qty = models.IntegerField(
		default = 0,
		validators=[MinValueValidator(0),]
	)

	# Price is a snapshot in time since xchange rate would fluctuate overtime.
	price = models.FloatField(default = 0)

	def _is_editable(self):
		return self.fullfill_qty == 0
	is_editable = property(_is_editable)

	def _std_value(self):
		return self.qty*self.price
	std_value = property(_std_value)

	def _discount_price(self):
		return self.price*(1-self.order.discount)
	discount_price = property(_discount_price)

	def _you_save(self):
		return self.price*self.order.discount
	you_save = property(_you_save)
	
	def _discount_value(self):
		if self.order.is_sold_at_cost: return self.item.item.converted_cost
		else: return self.std_value * (1-self.order.discount)
	discount_value = property(_discount_value)

	def _fullfill_qty(self):
		qty=MySalesOrderFullfillmentLineItem.objects.filter(so_line_item=self).values_list('fullfill_qty',flat=True)
		return sum(qty)
	fullfill_qty = property(_fullfill_qty)

	def _fullfill_rate(self):
		return self.fullfill_qty/self.qty
	fullfill_rate = property(_fullfill_rate)

	def _qty_balance(self):
		return self.qty - self.fullfill_qty
	qty_balance = property(_qty_balance)

class MySalesOrderFullfillment(models.Model):
	'''
	Fullfillment would require an associated SO.
	'''
	so = models.ForeignKey('MySalesOrder')

	# PO is optional. Retail sales, for example, does not require a PO.
	po = models.ForeignKey(
		'MyPurchaseOrder',
		blank = True,
		null = True
	)
	created_on = models.DateField(auto_now_add = True)
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = ''
	)

	def __unicode__(self):
		return '%s/F%02d'%(self.so.code,self.id)

	def _qty(self):
		return sum([f.fullfill_qty for f in MySalesOrderFullfillmentLineItem.objects.filter(so_fullfillment=self)])
	qty = property(_qty)

class MySalesOrderFullfillmentLineItem(models.Model):
	so_fullfillment = models.ForeignKey('MySalesOrderFullfillment')
	po_line_item = models.ForeignKey(
		'MyPurchaseOrderLineItem',
		null = True,
		blank = True
	)
	so_line_item = models.ForeignKey('MySalesOrderLineItem')
	fullfill_qty = models.IntegerField(
		default = 0,
		validators=[MinValueValidator(0),]
	)

class MySalesOrderPayment(models.Model):
	PAYMENT_METHOD_CHOICES = (
		('Cash','Cash'),
		('Paypal','Paypal'),
		(u'支付宝',u'支付宝'),
		(u'微信支付',u'微信支付'),
	)
	created_on = models.DateField(auto_now_add = True)

	# instance fields
	created_by = models.ForeignKey (
		User,
		null = True,
		blank = True,
		verbose_name = u'创建用户',
		help_text = '',
		related_name = 'Logger'
	)
	reviewed_by = models.ForeignKey(
		User,
		null = True,
		blank = True,
		default = None,
		related_name = "Reviewer"
	)	
	reviewed_on = models.DateField(
		null = True,
		blank = True,
		default = None
	)
	last_modified_on = models.DateField(auto_now = True)

	so = models.ForeignKey('MySalesOrder')
	amount = models.FloatField(default=0)
	payment_method = models.CharField(
		max_length = 16,
		default = 'Cash',
		choices = PAYMENT_METHOD_CHOICES
	)

	'''
	Deposit is different from regular payment because
	this money may be part of an agreement on what we can do with it.
	'''
	PAYMENT_USAGE_CHOICES = (
		('pay','Pay for a sales order'),
		('deposit','Deposit for a sales order'),
	)
	usage = models.CharField(
		max_length = 32,
		default = 'pay',
		choices = PAYMENT_USAGE_CHOICES
	)

	def __unicode__(self):
		return '%s/P%02d'%(self.so.code,self.id)

	def _is_editable(self):
		return not self.review_by
	is_editable = property(_is_editable)

	def _is_deposit(self):
		return self.usage == 'deposit'
	is_deposit = property(_is_deposit)

class MyPurchaseOrder(MyBaseModel):
	'''
	Attachment will be invoice, packing list, shipment info.
	'''

	# There is always a SO linked to a PO!
	# For WH PO, we will still create a SO, using SH or SZ as client.
	# This enforces payment settlement between even internal parties.
	so = models.ForeignKey('MySalesOrder')
	vendor = models.ForeignKey('MyCRM')
	created_on = models.DateField(auto_now_add = True)

	# instance fields
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = ''
	)

class MyPurchaseOrderLineItem(models.Model):
	ESTIMATED_MONTH_CHOICES = (
		(u'UNKNOWN',u'UNKNOWN'),
		(u'LOCAL',u'LOCAL'),
		(u'NEVER',u'NEVER'),
		(u'JAN',u'JAN'),
		(u'FEB',u'FEB'),
		(u'MAR',u'MAR'),
		(U'APR',u'APR'),
		(U'MAY',u'MAY'),
		(U'JUN',u'JUN'),
		(U'JUL',u'JUL'),
		(U'AUG',u'AUG'),
		(U'SEP',u'SEP'),
		(U'OCT',u'OCT'),
		(U'NOV',u'NOV'),
		(U'DEC',u'DEC'),
	)
	po = models.ForeignKey('MyPurchaseOrder')
	so_line_item = models.ForeignKey('MySalesOrderLineItem')
	invoiced_qty = models.IntegerField(default = 0)
	packinglist_qty = models.IntegerField(default = 0)
	available_in = models.CharField(
		max_length = 8,
		null = True,
		blank = True,
		choices = ESTIMATED_MONTH_CHOICES
	)
