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
from annoying.fields import JSONField  # django-annoying
from django.db.models import Q
from datetime import datetime as dt
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from localflavor.us.forms import USPhoneNumberField

######################################################
#
#	Global variables
#
#####################################################
ITEM_TYPE_CHOICES = (
    ('New', 'New'),
    ('Refurbished', 'Reburshied'),
    ('Defect', 'Defect'),
    ('Sample', 'Sample')
)
ESTIMATED_MONTH_CHOICES = (
    (u'UNKNOWN', u'UNKNOWN'),
    (u'LOCAL', u'LOCAL'),
    (u'NEVER', u'NEVER'),
    (u'JAN', u'JAN'),
    (u'FEB', u'FEB'),
    (u'MAR', u'MAR'),
    (U'APR', u'APR'),
    (U'MAY', u'MAY'),
    (U'JUN', u'JUN'),
    (U'JUL', u'JUL'),
    (U'AUG', u'AUG'),
    (U'SEP', u'SEP'),
    (U'OCT', u'OCT'),
    (U'NOV', u'NOV'),
    (U'DEC', u'DEC'),
)
######################################################
#
#	Abstract models
#
#####################################################


class MyBaseModel (models.Model):
    # fields
    hash = models.CharField(
        max_length=256,  # we don't expect using a hash more than 256-bit long!
        null=True,
        blank=True,
        default='',
        verbose_name=u'MD5 hash'
    )

    # basic value fields
    name = models.CharField(
        default=None,
        max_length=128,
        verbose_name=u'名称'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=u'描述'
    )
    abbrev = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name=u'Abbreviation'
    )

    # help text
    help_text = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=u'帮助提示'
    )

    # attachments
    attachments = GenericRelation('Attachment')
    notes = GenericRelation('MyNote')

    # is object active
    is_active = models.BooleanField(default=True)

    # this is an Abstract model
    class Meta:
        abstract = True

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
        default='',
        max_length=16,
        verbose_name=u'Tag'
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
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text=''
    )

    # basic value fields
    name = models.CharField(
        default='default name',
        max_length=64,
        verbose_name=u'附件名称'
    )
    description = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default='',
        verbose_name=u'附件描述'
    )
    file = models.FileField(
        upload_to='%Y/%m/%d',
        verbose_name=u'附件',
        help_text=u'附件'
    )
    file_base64 = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text=u'Based64 encoded file data'
    )
    thumbnail = models.FileField(
        null=True,
        blank=True,
        upload_to='%Y/%m/%d',
        verbose_name=u'Thumbnails',
        help_text=u'Thumbnails'
    )
    thumbnail_base64 = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text=u'Base64 encoded thumbnail data'
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
        verbose_name=u'Note'
    )

######################################################
#
#	App specific models
#
#####################################################


class MyCountry(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name=u'Country name'
    )
    abbrev = models.CharField(
        max_length=16,
        verbose_name=u'Country abbrev'
    )

    def __unicode__(self):
        return self.name


class MyCurrency(models.Model):
    name = models.CharField(
        max_length=16,
        verbose_name=u'Currency name'
    )
    abbrev = models.CharField(
        max_length=8,
        verbose_name=u'Currency abbrev'
    )
    symbol = models.CharField(
        max_length=8,
        verbose_name=u'Currency symbol'
    )
    country = models.ForeignKey(
        'MyCountry'
    )

    def __unicode__(self):
        return self.symbol


class MyExchangeRate(models.Model):
    home = models.ForeignKey('MyCurrency', related_name='home_currency')
    foreign = models.ForeignKey('MyCurrency', related_name='foreign_currency')
    rate = models.FloatField(
        default=1.0,
        verbose_name=u'Exchange rate'
    )

    def __unicode__(self):
        return u'%s = %s * %s' % (self.home, str(self.rate), self.foreign)


class MyUOM(models.Model):
    uom = models.CharField(
        max_length=8,
        verbose_name=u'unit of measure'
    )
    description = models.TextField(
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return self.uom


class MyFiscalYear(models.Model):
    begin = models.DateField(
        verbose_name=u'Fiscial year start'
    )
    end = models.DateField(
        verbose_name=u'Fiscal year end'
    )
    is_active = models.BooleanField(
        default=False,
    )

    def __unicode__(self):
        return '%s - %s' % (self.begin, self.end)


class MyCompany(MyBaseModel):
    home_currency = models.ForeignKey('MyCurrency')
    fiscal_year = models.ForeignKey('MyFiscalYear')

    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        verbose_name=u'Company phone'
    )


class MyLocation (models.Model):
    crm = models.ForeignKey('MyCRM')
    name = models.CharField(
        max_length=32,
        verbose_name=u'名称'
    )
    address = models.TextField(default='')
    users = models.ManyToManyField(User, null=True, blank=True)
    abbrev = models.CharField(
        max_length=5,
        null=True,
        blank=True,
    )
    is_primary = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s-%s' % (self.crm, self.name)

    def _code(self):
        return u'LOC%04d' % self.id
    code = property(_code)

    def _primary_storage(self):
        primary, created = MyStorage.objects.get_or_create(
            location=self, is_primary=True)
        return primary
    primary_storage = property(_primary_storage)

    def _inv_items(self):
        return MyItemInventory.objects.filter(storage__location=self)
    inv_items = property(_inv_items)

    def _storages(self):
        return MyStorage.objects.filter(location=self)
    storages = property(_storages)

    def _vendors(self):
        return reduce(lambda x, y: x + y, [s.vendors for s in self.storages])
    vendors = property(_vendors)


class MyStorage (models.Model):
    location = models.ForeignKey('MyLocation')
    is_primary = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s-%s' % (self.location, self.code)

    def _code(self):
        return u'STORG%04d (%s)' % (self.id, self.location.abbrev)
    code = property(_code)

    def _physical(self):
        qty = [
            inv_item.physical for inv_item in MyItemInventory.objects.filter(storage=self)]
        return sum(qty)
    physical = property(_physical)

    def _theoretical(self):
        qty = [inv_item.theoretical for inv_item in MyItemInventory.objects.filter(
            storage=self)]
        return sum(qty)
    theoretical = property(_theoretical)

    def _inv_items(self):
        return MyItemInventory.objects.filter(storage=self)
    inv_items = property(_inv_items)

    def _vendors(self):
        vendor_ids = set(self.inv_items.values_list('item__brand', flat=True))
        return MyCRM.objects.filter(id__in=vendor_ids).order_by('name')
    vendors = property(_vendors)

    def _seasons(self):
        season_ids = set(self.inv_items.values_list('item__season', flat=True))
        return MySeason.objects.filter(id__in=season_ids).order_by('name')
    seasons = property(_seasons)

###################################################
#
#	CRM models
#
###################################################


class MyCRMCustomManager(models.Manager):

    def vendors(self):
        return self.get_queryset().filter(Q(crm_type='V') | Q(crm_type='B'))

    def customers(self):
        return self.get_queryset().filter(Q(crm_type='C') | Q(crm_type='B'))

    def vendor_need_invoice(self):
        vendor_ids = set([x.vendor.id for x in filter(
            lambda x: x.fulfill_qty < x.order_qty, MyPurchaseOrder.objects.filter(vendor__in=self.vendors()))])
        return self.get_queryset().filter(id__in=vendor_ids)


class MyCRM(MyBaseModel):
    # custom managers
    # Note: the 1st one defined will be taken as the default!
    objects = MyCRMCustomManager()

    CRM_TYPE_CHOICES = (
        ('B', 'Both'),  # can only be WH internals
        ('V', 'Vendor'),  # can only  link to PO
        ('C', 'Customer')  # can only link to SO
    )
    crm_type = models.CharField(
        max_length=16,
        default='vendor',
        choices=CRM_TYPE_CHOICES
    )
    contact = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name=u'CRM contact'
    )
    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        verbose_name=u'Vendor phone'
    )
    url = models.URLField(
        null=True,
        blank=True,
        default='',
    )
    currency = models.ForeignKey('MyCurrency')
    std_discount = models.FloatField(
        default=0.25,
        validators=[MaxValueValidator(1.0), MinValueValidator(0.0)]
    )

    def __unicode__(self):
        return self.name

    def _code(self):
        return '%04d' % self.id
    code = property(_code)

    def _account_receivable(self):
        # how much they owe us
        return sum([x.account_receivable for x in MySalesOrder.objects.filter(customer=self)])
    account_receivable = property(_account_receivable)

    def _account_payable(self):
        # how much we owe them
        return sum([x.account_payable for x in MyPurchaseOrder.objects.filter(vendor=self)])
    account_payable = property(_account_payable)

    def _balance(self):
        return self.account_payable - self.account_receivable
    balance = property(_balance)

    def _avartar(self):
        try:
            return self.attachments.all()[0]
        except:
            return None
    avartar = property(_avartar)

###################################################
#
#	Product models
#
###################################################


class MySeason(models.Model):
    name = models.CharField(
        max_length=8
    )

    def __unicode__(self):
        return self.name

    def _vendors(self):
        brand_ids = set(
            MyItem.objects.filter(season=self).values_list('brand', flat=True))
        return MyCRM.objects.filter(id__in=brand_ids).order_by('name')
    vendors = property(_vendors)

    def _vendor_count(self):
        return self.vendors.count()
    vendor_count = property(_vendor_count)

    def _items(self):
        return MyItem.objects.filter(season=self).order_by('name')
    items = property(_items)

    def _item_count(self):
        return self.items.count()
    item_count = property(_item_count)


class MySizeChart(models.Model):
    # CSV format, eg "S,M,L", "0,2,4,6","XS,S,M,L,XL"
    size = models.CharField(
        max_length=128
    )

    def __unicode__(self):
        return self.size


class MyVendorItem(models.Model):
    vendor = models.ForeignKey('MyCRM')
    currency = models.ForeignKey('MyCurrency')
    product = models.ForeignKey('MyItem')

    # This is vendor SKU
    sku = models.CharField(
        max_length=32,
        default='',
        null=True,
        blank=True
    )
    price = models.FloatField(
        default=0,
        validators=[MinValueValidator(0.0), ]
    )
    msrp = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), ],
        verbose_name=u'MSRP'
    )

    # If we know when is the deadline to place SO
    # against this item. This is observed when showing items
    # available for SO on e-Commerce site.
    order_deadline = models.DateField(
        null=True,
        blank=True,
    )

    # Minimal qty per line item
    minimal_qty = models.IntegerField(default=1)

    def _discount(self):
        if self.msrp:
            return (self.msrp - self.price) / self.msrp
        else:
            return ''
    discount = property(_discount)


class MyItem(MyBaseModel):

    '''
    Attachment would be item photos.
    '''
    season = models.ForeignKey('MySeason')
    brand = models.ForeignKey('MyCRM', verbose_name=u'品牌')
    color = models.CharField(
        max_length=128,
        default='',
    )
    price = models.FloatField(
        default=0,
        validators=[MinValueValidator(0.0), ]
    )  # retail price
    currency = models.ForeignKey('MyCurrency')

    # size chart
    size_chart = models.ForeignKey(
        'MySizeChart',
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s | %s' % (self.name, self.color)

    def _code(self):
        return u'%s-%s' % (self.name, self.color)
    code = property(_code)

    def _product_id(self):
        return '%06d' % self.id
    product_id = property(_product_id)

    def _available_left_in_days():
        if self.order_deadline:
            return (dt.now() - self.order_deadline).days
        else:
            return '-'
    available_left_in_days = property(_available_left_in_days)

    def _converted_cost(self):
        vendor_item = MyVendorItem.objects.filter(
            product=self, vendor=self.brand)
        if len(vendor_item):
            vendor_item = vendor_item[0]
        else:
            return 0

        exchange_rate = None
        converted_cost = 0
        try:
            exchange_rate = MyExchangeRate.objects.get(
                home=self.currency, foreign=vendor_item.currency)
            converted_cost = vendor_item.price / exchange_rate.rate
        except:
            pass

        if not exchange_rate:
            try:
                exchange_rate = MyExchangeRate.objects.get(
                    foreign=self.currency, home=vendor_item.currency)
                converted_cost = vendor_item.price * exchange_rate.rate
            except:
                pass
        return converted_cost
    converted_cost = property(_converted_cost)

    def _multiplier(self):
        if self.converted_cost:
            return self.price / self.converted_cost
        else:
            return None
    multiplier = property(_multiplier)

    def _total_physical(self):
        return sum([qty for size, qty in self.physical])
    total_physical = property(_total_physical)

    def _physical(self):
        qty = []
        for inv_item in MyItemInventory.objects.filter(item=self):
            if inv_item.withdrawable:
                qty.append((inv_item.size, inv_item.physical))
        return qty
    physical = property(_physical)

    def _total_theoretical(self):
        return sum([qty for size, qty in self.theoretical])
    total_theoretical = property(_total_theoretical)

    def _theoretical(self):
        qty = []
        for inv_item in MyItemInventory.objects.filter(item=self).order_by('size'):
            qty.append((inv_item.size, inv_item.theoretical))
        return qty
    theoretical = property(_theoretical)

    def _is_so_ready(self):
        '''
        Item is SO ready if the following conditions are met:
        1. has a known price: price > 0, and
        2. physical > 0 (have some in local stock), or has a known vendor price (can be ordered)
        '''
        return self.price > 0 and (self.physical > 0 or self.converted_cost > 0)
    is_so_ready = property(_is_so_ready)

    def _is_po_ready(self):
        '''
        Item is PO ready if the following conditions are met:
        1. has a known vendor price (can be ordered)
        '''
        return self.converted_cost > 0
    is_po_ready = property(_is_po_ready)

    def _sizes(self):
        return [x.size for x in filter(lambda x: x.is_so_ready, self.myiteminventory_set.all())]
    sizes = property(_sizes)

    def _avartar(self):
        try:
            return self.attachments.all()[0]
        except:
            return None
    avartar = property(_avartar)

    def _season_name(self):
        return self.season.name
    season_name = property(_season_name)

###################################################
#
#	Inventory models
#
###################################################


class MyItemInventoryCustomManager(models.Manager):

    def rank_by_so_qty(self, top=10):
        tmp = filter(
            lambda x: x.on_so_qty, self.get_queryset().filter(item_type='New'))
        return list(reversed(sorted(tmp, lambda x, y: cmp(x.on_so_qty, y.on_so_qty))))[:top]

    def rank_by_po_qty(self, top=10):
        tmp = filter(
            lambda x: x.on_po_qty, self.get_queryset().filter(item_type='New'))
        return list(reversed(sorted(tmp, lambda x, y: cmp(x.on_po_qty, y.on_po_qty))))[:top]

    def rank_by_fulfill_profit(self, top=10):
        tmp = filter(lambda x: x.fulfill_profit, self.get_queryset())
        return list(reversed(sorted(tmp, lambda x, y: cmp(x.fulfill_profit, y.fulfill_profit))))[:top]


class MyItemInventory(models.Model):
    objects = MyItemInventoryCustomManager()

    item = models.ForeignKey('MyItem')
    size = models.CharField(
        max_length=4,
        default=''
    )
    storage = models.ForeignKey('MyStorage')
    withdrawable = models.BooleanField(default=True)

    physical = models.PositiveIntegerField(
        default=0,
    )

    # This allows us to deactivate individual size
    is_active = models.BooleanField(default=True)

    # Item type
    item_type = models.CharField(
        max_length=16,
        default='New',
        choices=ITEM_TYPE_CHOICES
    )

    def __unicode__(self):
        return self.code

    def _code(self):
        return 'INV-%06d' % self.id
    code = property(_code)

    def _theoretical(self):
        inv = 0
        for audit in MyItemInventoryTheoreticalAudit.objects.filter(inv=self):
            if audit.out:
                inv -= audit.qty
            else:
                inv += audit.qty
        return inv
    theoretical = property(_theoretical)

    def _is_so_ready(self):
        if self.item_type in ['New', 'Refurbished']:
            return True
        else:
            return False
    is_so_ready = property(_is_so_ready)

    def _on_po_qty(self):
        return sum(MyPurchaseOrderLineItem.objects.filter(inv_item=self).values_list('qty', flat=True))
    on_po_qty = property(_on_po_qty)

    def _on_so_qty(self):
        return sum(MySalesOrderLineItem.objects.filter(item=self).values_list('qty', flat=True))
    on_so_qty = property(_on_so_qty)

    def _fulfill_profit(self):
        return sum([x.fulfill_profit for x in MySalesOrderLineItem.objects.filter(item=self) if x.fulfill_profit])
    fulfill_profit = property(_fulfill_profit)


class MyItemInventoryPhysicalAudit(models.Model):
    created_on = models.DateField(auto_now_add=True)

    # instance fields
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Auditor',
        help_text=''
    )
    inv = models.ForeignKey('MyItemInventory')
    physical = models.PositiveIntegerField(default=0)
    theoretical = models.IntegerField(default=0)

    def _diff(self):
        return self.physical - self.theoretical
    diff = property(_diff)

    def _is_clean(self):
        return self.diff == 0
    is_clean = property(_is_clean)


class MyItemInventoryTheoreticalAudit(models.Model):
    created_on = models.DateField(auto_now_add=True)

    # instance fields
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Auditor',
        help_text=''
    )

    # Against this inventory we are adjusting
    inv = models.ForeignKey('MyItemInventory')

    # If True, we are depleting qty.
    out = models.BooleanField(default=False)
    qty = models.IntegerField(default=0)

    # Link to actions tat caused inventory change
    # generic foreign key to base model
    # so we can link attachment to any model defined below
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    reason = models.TextField(default='')

###################################################
#
#	Sales order models
#
###################################################


class MyBusinessModel(MyBaseModel):

    '''
    Define sales model that business supports.
    '''
    SALES_MODEL_CHOICES = (
        ('Retail', u'零售'),
        ('Wholesale', u'批发'),
        ('Consignment', u'代销'),
        ('Leasing', u'租赁'),
        ('Proxy', u'订货'),
    )
    sales_model = models.CharField(
        max_length=64,
        default='Retail',
        choices=SALES_MODEL_CHOICES
    )

    def __unicode__(self):
        return self.sales_model

    def _process_model(self):
        if self.sales_model in ['Retail', 'Wholesale']:
            return 1
        elif self.sales_model in ['Proxy', ]:
            return 2
        elif self.sales_model in ['Consignment', ]:
            return 3
        elif self.sales_model in ['Leasing', ]:
            return 4
    process_model = property(_process_model)


class MySalesOrderCustomManager(models.Manager):

    def rank_by_qty_balance(self, top=10, reverse=False):
        tmp = filter(lambda x: x.qty_balance, self.get_queryset())
        if reverse:
            return list(reversed(sorted(tmp, lambda x, y: cmp(x.qty_balance, y.qty_balance))))[:top]
        else:
            return list(sorted(tmp, lambda x, y: cmp(x.qty_balance, y.qty_balance)))[:top]

    def rank_by_fulfill_rate_by_qty(self, top=10, reverse=False):
        tmp = filter(
            lambda x: x.fulfill_rate_by_qty and x.fulfill_rate_by_qty < 100, self.get_queryset())

        if reverse:
            return list(reversed(sorted(tmp, lambda x, y: cmp(x.fulfill_rate_by_qty, y.fulfill_rate_by_qty))))[:top]
        else:
            return list(sorted(tmp, lambda x, y: cmp(x.fulfill_rate_by_qty, y.fulfill_rate_by_qty)))[:top]

    def zero_fulfill(self):
        return filter(lambda x: x.fulfill_rate_by_qty == 0, self.get_queryset())


class MySalesOrder(models.Model):
    objects = MySalesOrderCustomManager()

    business_model = models.ForeignKey('MyBusinessModel')
    customer = models.ForeignKey('MyCRM')
    sales = models.ForeignKey(User, related_name='sales')
    default_storage = models.ForeignKey('MyStorage', null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text='',
        related_name='logger'
    )
    discount = models.FloatField(
        validators=[MaxValueValidator(1.0), MinValueValidator(0.0), ]
    )

    # Set this flag to True for internal customers.
    # This will force line item price to use item's converted cost instead of
    # RP.
    is_sold_at_cost = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s for %s' % (self.code, self.customer)

    def _code(self):
        if self.default_storage:
            return '%s%d-%04d' % (self.default_storage.location.abbrev, dt.now().year, self.id)
        else:
            return '%s%d-%04d' % (self.default_storage, dt.now().year, self.id)
    code = property(_code)

    def _is_editable(self):
        '''
        Sales order becomes locked when there has been fulfillment or a payment.
        Since return is only available when there has been fulfillments, it is
        sufficient to check fulfillment.
        '''
        return self.total_payment == 0 and self.fulfill_qty == 0
    is_editable = property(_is_editable)

    def _life_in_days(self):
        return (dt.now() - self.created_on).days
    life_in_days = property(_life_in_days)

    def _line_item_qty(self):
        return len(MySalesOrderLineItem.objects.filter(order=self).values_list('id', flat=True))
    line_item_qty = property(_line_item_qty)

    def _total_qty(self):
        return sum(MySalesOrderLineItem.objects.filter(order=self).values_list('qty', flat=True))
    total_qty = property(_total_qty)

    def _total_std_value(self):
        return sum([line.std_value for line in MySalesOrderLineItem.objects.filter(order=self)])
    total_std_value = property(_total_std_value)

    def _total_discount_value(self):
        return sum([line.discount_value for line in MySalesOrderLineItem.objects.filter(order=self)])
    total_discount_value = property(_total_discount_value)

    def _implied_discount(self):
        if self.total_std_value:
            return 1 - self.total_discount_value / self.total_std_value
        else:
            return ''
    implied_discount = property(_implied_discount)

    def _fulfill_qty(self):
        return sum([line.fulfill_qty for line in MySalesOrderLineItem.objects.filter(order=self)])
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_std_value(self):
        return sum([line.fulfill_qty * line.price for line in MySalesOrderLineItem.objects.filter(order=self)])
    fulfill_std_value = property(_fulfill_std_value)

    def _fulfill_discount_value(self):
        return sum([line.fulfill_qty * line.discount_price for line in MySalesOrderLineItem.objects.filter(order=self)])
    fulfill_discount_value = property(_fulfill_discount_value)

    def _fulfill_rate_by_qty(self):
        if self.total_qty:
            return self.fulfill_qty * 100.0 / self.total_qty
        else:
            return ''
    fulfill_rate_by_qty = property(_fulfill_rate_by_qty)

    def _fulfill_rate_by_value(self):
        if self.total_std_value:
            return self.fulfill_std_value * 100.0 / self.total_std_value
        else:
            return ''
    fulfill_rate_by_value = property(_fulfill_rate_by_value)

    def _last_fulfill_date(self):
        try:
            return MySalesOrderFulfillment.objects.filter(so=self).order_by('-created_on')[0].created_on
        except:
            return ''
    last_fulfill_date = property(_last_fulfill_date)

    def _fulfillments(self):
        return MySalesOrderFulfillment.objects.filter(so=self).order_by('created_on')
    fulfillments = property(_fulfillments)

    def _discount_in_pcnt(self):
        return '%d%%' % (self.discount * 100)
    discount_in_pcnt = property(_discount_in_pcnt)

    def _payments(self):
        return MySalesOrderPayment.objects.filter(so=self)
    payments = property(_payments)

    def _total_payment(self):
        return sum([p.amount for p in MySalesOrderPayment.objects.filter(so=self)])
    total_payment = property(_total_payment)

    def _qty_balance(self):
        return self.total_qty - self.fulfill_qty + self.return_qty
    qty_balance = property(_qty_balance)

    def _returns(self):
        return MySalesOrderReturn.objects.filter(so=self).order_by('created_on')
    returns = property(_returns)

    def _return_qty(self):
        return sum([r.return_qty for r in MySalesOrderReturn.objects.filter(so=self)])
    return_qty = property(_return_qty)

    def _credit(self):
        return sum([r.credit for r in MySalesOrderReturn.objects.filter(so=self)])
    credit = property(_credit)

    def _refundable_qty(self):
        return sum([r.refundable_qty for r in MySalesOrderReturn.objects.filter(so=self)])
    refundable_qty = property(_refundable_qty)

    def _account_receivable(self):
        '''
        AR is computed by actual fulfilled value instead of what's on order.
        '''
        return self.fulfill_discount_value - (self.total_payment)
    account_receivable = property(_account_receivable)

    def _vendors(self):
        ids = list(set(MySalesOrderLineItem.objects.filter(
            order=self).values_list('item__item__brand', flat=True)))
        return MyCRM.objects.vendors().filter(id__in=ids)
    vendors = property(_vendors)

    def _is_po_needed(self):
        '''
        SO needs PO if the following conditions are met:
        1. Business model is Proxy
        2. PO do not exist yet
        '''
        existing = MyPurchaseOrder.objects.filter(
            so=self, vendor__in=self.vendors)
        return self.business_model.process_model == 2 and len(existing) == 0
    is_po_needed = property(_is_po_needed)

    def _fulfill_cost(self):
        return sum([x.fulfill_cost for x in MySalesOrderLineItem.objects.filter(order=self) if x.fulfill_cost])
    fulfill_cost = property(_fulfill_cost)

    def _fulfill_profit(self):
        return sum([x.fulfill_profit for x in MySalesOrderLineItem.objects.filter(order=self) if x.fulfill_profit])
    fulfill_profit = property(_fulfill_profit)


class MySalesOrderLineItem(models.Model):
    order = models.ForeignKey('MySalesOrder')
    item = models.ForeignKey('MyItemInventory')
    qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), ]
    )

    # Price is a snapshot in time since xchange rate would fluctuate overtime.
    price = models.FloatField(default=0)

    def _is_editable(self):
        return self.fulfill_qty == 0
    is_editable = property(_is_editable)

    def _std_value(self):
        return self.qty * self.price
    std_value = property(_std_value)

    def _discount_price(self):
        return self.price * (1 - self.order.discount)
    discount_price = property(_discount_price)

    def _you_save(self):
        return self.price * self.order.discount
    you_save = property(_you_save)

    def _discount_value(self):
        if self.order.is_sold_at_cost:
            return self.item.item.converted_cost
        else:
            return self.std_value * (1 - self.order.discount)
    discount_value = property(_discount_value)

    def _fulfill_qty(self):
        qty = MySalesOrderFulfillmentLineItem.objects.filter(
            so_line_item=self).values_list('fulfill_qty', flat=True)
        return sum(qty) - self.refundable_qty
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_rate(self):
        return self.fulfill_qty / self.qty
    fulfill_rate = property(_fulfill_rate)

    def _qty_balance(self):
        return self.qty - self.fulfill_qty
    qty_balance = property(_qty_balance)

    def _return_qty(self):
        return sum(MySalesOrderReturnLineItem.objects.filter(so_line_item=self).values_list('return_qty', flat=True))
    return_qty = property(_return_qty)

    def _credit(self):
        return sum(MySalesOrderReturnLineItem.objects.filter(so_line_item=self, reason__is_refundable=True).values_list('credit', flat=True))
    credit = property(_credit)

    def _refundable_qty(self):
        return sum(MySalesOrderReturnLineItem.objects.filter(so_line_item=self, reason__is_refundable=True).values_list('return_qty', flat=True))
    refundable_qty = property(_refundable_qty)

    def _fulfill_cost(self):
        cost = self.item.item.converted_cost
        if cost:
            return self.fulfill_qty * cost
        else:
            return None
    fulfill_cost = property(_fulfill_cost)

    def _fulfill_profit(self):
        cost = self.item.item.converted_cost
        if cost:
            unit_profit = self.discount_price - cost
            return self.fulfill_qty * unit_profit
        else:
            return None
    fulfill_profit = property(_fulfill_profit)


class MySalesOrderFulfillment(models.Model):

    '''
    Fulfillment would require an associated SO.
    '''
    so = models.ForeignKey('MySalesOrder')

    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text='',
        related_name="so_fulfillment_loggers"
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True,
        default=None
    )
    reviewed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Reviewer',
        help_text='',
        related_name='so_fulfillment_reviewers'
    )

    def __unicode__(self):
        return '%s/%s' % (self.so.code, self.code)

    def _code(self):
        return 'SOFF%3d' % self.id
    code = property(_code)

    def _qty(self):
        return sum([f.fulfill_qty for f in MySalesOrderFulfillmentLineItem.objects.filter(so_fulfillment=self)])
    qty = property(_qty)

    def _value(self):
        return sum([f.fulfill_value for f in MySalesOrderFulfillmentLineItem.objects.filter(so_fulfillment=self)])
    value = property(_value)

    def _is_editable(self):
        return self.reviewed_on is None
    is_editable = property(_is_editable)


class MySalesOrderFulfillmentLineItem(models.Model):
    so_fulfillment = models.ForeignKey('MySalesOrderFulfillment')
    so_line_item = models.ForeignKey('MySalesOrderLineItem')
    fulfill_qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), ]
    )

    def _fulfill_value(self):
        return self.fulfill_qty * self.so_line_item.price
    fulfill_value = property(_fulfill_value)

    def _max_qty(self):
        '''
        If to edit this record, max_qty holds the current max qty balance including
        what is currently saved in this recorded as fulfilled.
        '''
        return self.so_line_item.qty_balance + self.fulfill_qty
    max_qty = property(_max_qty)

###################################################
#
#	Sales order turn models
#
###################################################


class MyReturnReason(MyBaseModel):
    CATEGORY_CHOICES = (
        ('Small', 'Sizing too small'),
        ('Large', 'Sizing too large'),
        ('Quality', 'Quality/Satisfaction'),
        ('Color', 'Color'),
        ('Service', 'Service'),
    )
    is_refundable = models.BooleanField(default=True)
    result_type = models.CharField(
        max_length=16,
        default='Refurbished',
        choices=ITEM_TYPE_CHOICES
    )
    category = models.CharField(
        max_length=16,
        choices=CATEGORY_CHOICES
    )
    code = models.CharField(
        max_length=8,
        default='',
        unique=True
    )

    def __unicode__(self):
        if self.is_refundable:
            return '* %s' % (self.description)
        else:
            return self.description


class MySalesOrderReturn(models.Model):
    so = models.ForeignKey('MySalesOrder')
    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text='',
        related_name='so_return_loggers'
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True,
        default=None
    )
    reviewed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Reviewer',
        help_text='',
        related_name='so_return_reviewers'
    )

    def __unicode__(self):
        return '%s/%s' % (self.so.code, self.code)

    def _code(self):
        return 'SORTN%3d' % self.id
    code = property(_code)

    def _return_qty(self):
        return sum([i.return_qty for i in MySalesOrderReturnLineItem.objects.filter(so_return=self)])
    return_qty = property(_return_qty)

    def _credit(self):
        return sum([i.credit for i in MySalesOrderReturnLineItem.objects.filter(so_return=self, reason__is_refundable=True)])
    credit = property(_credit)

    def _refundable_qty(self):
        return sum([i.return_qty for i in MySalesOrderReturnLineItem.objects.filter(so_return=self, reason__is_refundable=True)])
    refundable_qty = property(_refundable_qty)

    def _is_editable(self):
        return self.reviewed_on is None
    is_editable = property(_is_editable)


class MySalesOrderReturnLineItem(models.Model):
    so_return = models.ForeignKey('MySalesOrderReturn')
    so_line_item = models.ForeignKey('MySalesOrderLineItem')
    return_qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), ]
    )
    reason = models.ForeignKey('MyReturnReason')
    credit = models.FloatField(default=0)

    def _max_qty(self):
        return self.so_line_item.fulfill_qty + self.return_qty
    max_qty = property(_max_qty)

###################################################
#
#	Sales order payment models
#
###################################################


class MySalesOrderPayment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('Paypal', 'Paypal'),
        (u'支付宝', u'支付宝'),
        (u'微信支付', u'微信支付'),
    )
    created_on = models.DateField(auto_now_add=True)

    # instance fields
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        verbose_name=u'创建用户',
        help_text='',
        related_name='Logger'
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        default=None,
        related_name="Reviewer"
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True,
        default=None
    )
    last_modified_on = models.DateField(auto_now=True)

    so = models.ForeignKey('MySalesOrder')
    amount = models.FloatField(default=0)
    payment_method = models.CharField(
        max_length=16,
        default='Cash',
        choices=PAYMENT_METHOD_CHOICES
    )

    '''
	Deposit is different from regular payment because
	this money may be part of an agreement on what we can do with it.
	'''
    PAYMENT_USAGE_CHOICES = (
        ('pay', 'Pay for a sales order'),
        ('deposit', 'Deposit for a sales order'),
    )
    usage = models.CharField(
        max_length=32,
        default='pay',
        choices=PAYMENT_USAGE_CHOICES
    )

    def __unicode__(self):
        return '%s/%s' % (self.so.code, self.code)

    def _code(self):
        return 'SOPAY%03d' % self.id
    code = property(_code)

    def _is_editable(self):
        return not self.reviewed_by
    is_editable = property(_is_editable)

    def _is_deposit(self):
        return self.usage == 'deposit'
    is_deposit = property(_is_deposit)

###################################################
#
#	Purchase order models
#
###################################################


class MyPurchaseOrder(models.Model):

    '''
    Attachment will be invoice, packing list, shipment info.
    '''
    # There is always a SO linked to a PO!
    # For WH PO, we will still create a SO, using SH or SZ as client.
    # This enforces payment settlement between even internal parties.
    so = models.ForeignKey(
        'MySalesOrder',
        null=True,
        blank=True,
        verbose_name=u'Associated sales order'
    )
    vendor = models.ForeignKey('MyCRM')
    location = models.ForeignKey('MyLocation')
    created_on = models.DateField(auto_now_add=True)

    # instance fields
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text=''
    )

    # order placed on
    placed_on = models.DateField(
        null=True,
        blank=True,
        verbose_name=u'Order placed on'
    )

    def __unicode__(self):
        return u'%s for %s' % (self.code, self.vendor)

    def _code(self):
        return 'PO%d-%04d' % (dt.now().year, self.id)
    code = property(_code)

    def _is_editable(self):
        return not self.placed_on
    is_editable = property(_is_editable)

    def _order_qty(self):
        return sum(MyPurchaseOrderLineItem.objects.filter(po=self).values_list('qty', flat=True))
    order_qty = property(_order_qty)

    def _available_in(self):
        return set(MyPurchaseOrderLineItem.objects.filter(po=self).values_list('available_in', flat=True))
    available_in = property(_available_in)

    def _line_items(self):
        return MyPurchaseOrderLineItem.objects.filter(po=self)
    line_items = property(_line_items)

    def _order_value(self):
        return sum(filter(lambda x: x is not None, [item.value for item in self.line_items]))
    order_value = property(_order_value)

    def _fulfill_qty(self):
        return sum([x.fulfill_qty for x in MyPOFulfillment.objects.filter(po=self)])
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_value(self):
        return sum([x.fulfill_value for x in MyPOFulfillment.objects.filter(po=self)])
    fulfill_value = property(_fulfill_value)

    def _fulfill_rate_by_qty(self):
        if self.order_qty:
            return self.fulfill_qty * 100.0 / self.order_qty
        else:
            return 0
    fulfill_rate_by_qty = property(_fulfill_rate_by_qty)

    def _fulfill_rate_by_value(self):
        if self.order_value:
            return self.fulfill_value * 100.0 / self.order_value
        else:
            return 0
    fulfill_rate_by_value = property(_fulfill_rate_by_value)

    def _account_payable(self):
        return self.order_value - self.fulfill_value
    account_payable = property(_account_payable)


class MyPurchaseOrderLineItem(models.Model):
    po = models.ForeignKey('MyPurchaseOrder')
    inv_item = models.ForeignKey('MyItemInventory')
    qty = models.PositiveIntegerField(default=1)
    available_in = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        choices=ESTIMATED_MONTH_CHOICES
    )

    def _price(self):
        item = self.inv_item.item
        vendor_items = MyVendorItem.objects.filter(
            vendor=self.po.vendor, product=item).order_by('price')
        if len(vendor_items):
            return vendor_items[0].price
        else:
            return None
    price = property(_price)

    def _value(self):
        if self.price:
            return self.price * self.qty
        else:
            return None
    value = property(_value)

    def _fulfill_qty(self):
        return sum(MyPOFulfillmentLineItem.objects.filter(po_line_item=self).values_list('fulfill_qty', flat=True))
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_value(self):
        return sum([x.fulfill_value for x in MyPOFulfillmentLineItem.objects.filter(po_line_item=self)])
    fulfill_value = property(_fulfill_value)

    def _fulfill_rate_by_qty(self):
        return self.fulfill_qty / self.qty * 100
    fulfill_rate_by_qty = property(_fulfill_rate_by_qty)

    def _fulfill_rate_by_value(self):
        if self.value:
            return self.fulfill_value / self.value
        else:
            return ''
    fulfill_rate_by_value = property(_fulfill_rate_by_value)


class MyPOFulfillment(models.Model):

    '''
    Fulfillment would require an associated PO.
    '''
    po = models.ForeignKey('MyPurchaseOrder')

    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text='',
        related_name="po_fulfillment_loggers"
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True,
        default=None
    )
    reviewed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Reviewer',
        help_text='',
        related_name='po_fulfillment_reviewers'
    )

    invoices = models.ManyToManyField('MyInvoice')

    def __unicode__(self):
        return '%s/%s' % (self.po.code, self.code)

    def _code(self):
        return 'POFF%3d' % self.id
    code = property(_code)

    def _qty(self):
        return sum(MyPOFulfillmentLineItem.objects.filter(po_fulfillment=self).values_list('fulfill_qty', flat=True))
    qty = property(_qty)

    def _value(self):
        return sum([f.fulfill_value for f in MyPOFulfillmentLineItem.objects.filter(po_fulfillment=self)])
    value = property(_value)

    def _is_editable(self):
        return self.reviewed_on is None
    is_editable = property(_is_editable)

    def _fulfill_qty(self):
        return sum(MyPOFulfillmentLineItem.objects.filter(po_fulfillment=self).values_list('fulfill_qty', flat=True))
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_value(self):
        return sum([x.fulfill_value for x in MyPOFulfillmentLineItem.objects.filter(po_fulfillment=self)])
    fulfill_value = property(_fulfill_value)


class MyPOFulfillmentLineItem(models.Model):
    po_fulfillment = models.ForeignKey('MyPOFulfillment')
    po_line_item = models.ForeignKey('MyPurchaseOrderLineItem')
    fulfill_qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), ]
    )
    invoice = models.ForeignKey('MyInvoice')

    def _fulfill_value(self):
        return self.fulfill_qty * self.po_line_item.price
    fulfill_value = property(_fulfill_value)

###################################################
#
#	Invoice models
#
###################################################


class MyInvoice(models.Model):
    crm = models.ForeignKey('MyCRM')
    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Invoice createed by',
        help_text='',
        related_name=u'invoice_loggers'
    )
    invoice_no = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=u'Invoice no.'
    )
    issued_on = models.DateField()
    gross_cost = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    maturity_date = models.DateField(
        null=True,
        blank=True
    )
    qty = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True
    )
    reviewed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Invoice reviewed by',
        help_text='',
        related_name=u'invoice_reviewers'
    )

    def __unicode__(self):
        return self.code

    def _code(self):
        if self.invoice_no:
            return '%s-%s' % (self.crm, self.invoice_no)
        else:
            return 'INVOICE%06d' % (self.id)
    code = property(_code)

    def _is_editable(self):
        return not self.reviewed_by
    is_editable = property(_is_editable)

    def _is_receivable(self):
        return self.is_editable and self.qty_balance_items_fulfill > 0
    is_receivable = property(_is_receivable)

    def _discount_value(self):
        return self.gross_cost * (1 - self.discount)
    discount_value = property(_discount_value)

    def _discount_in_pcnt(self):
        return '%d%%' % (self.discount * 100)
    discount_in_pcnt = property(_discount_in_pcnt)

    def _items_qty(self):
        # aggregated qty by line items
        return sum(MyInvoiceItem.objects.filter(invoice=self).values_list('qty', flat=True))
    items_qty = property(_items_qty)

    def _items_value(self):
        # aggregated value by line items
        values = filter(
            lambda x: x, [item.value for item in MyInvoiceItem.objects.filter(invoice=self)])
        return sum(values)
    items_value = property(_items_value)

    def _qty_delta(self):
        # diff between entered qty vs. line item sum
        return self.items_qty - self.qty
    qty_delta = property(_qty_delta)

    def _value_delta(self):
        # diff between entered value vs. line item sum
        return self.items_value - self.discount_value
    value_delta = property(_value_delta)

    def _fulfill_qty(self):
        return sum([x.fulfill_qty for x in MyInvoiceItem.objects.filter(invoice=self)])
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_value(self):
        return sum([x.fulfill_value for x in MyInvoiceItem.objects.filter(invoice=self)])
    fulfill_value = property(_fulfill_value)

    def _qty_balance_invoice_fulfill(self):
        # diff between entered invoice qty vs. line item fulfill
        return self.qty - self.fulfill_qty

    def _value_balance_invoice_fulfill(self):
        # diff between entered invoice value vs. line item fulfill
        return self.discount_value - self.fulfill_value

    def _qty_balance_items_fulfill(self):
        # diff between line item qty vs. fulfill
        return self.items_qty - self.fulfill_qty
    qty_balance_items_fulfill = property(_qty_balance_items_fulfill)

    def _value_balance_items_fulfill(self):
        # diff between line item value vs. fulfill
        return self.items - self.fulfill_value
    value_balance_items_fulfill = property(_value_balance_items_fulfill)

    def _fulfill_rate_by_invoice_qty(self):
        return self.fulfill_qty * 100.0 / self.qty
    fulfill_rate_by_invoice_qty = property(_fulfill_rate_by_invoice_qty)

    def _fulfill_rate_by_invoice_value(self):
        return self.fulfill_value * 100.0 / self.discount_value
    fulfill_rate_by_invoice_value = property(_fulfill_rate_by_invoice_value)

    def _fulfill_rate_by_items_qty(self):
        return self.fulfill_qty * 100.0 / self.items_qty
    fulfill_rate_by_items_qty = property(_fulfill_rate_by_items_qty)

    def _fulfill_rate_by_items_value(self):
        return self.fulfill_value * 100.0 / self.items_value
    fulfill_rate_by_items_value = property(_fulfill_rate_by_items_value)

    def _fulfillments(self):
        return MyInvoiceReceive.objects.filter(invoice=self)
    fulfillments = property(_fulfillments)


class MyInvoiceItem(models.Model):
    invoice = models.ForeignKey('MyInvoice')
    inv_item = models.ForeignKey('MyItemInventory')
    qty = models.PositiveIntegerField(default=1)

    def _vendor_item(self):
        vendor_items = MyVendorItem.objects.filter(
            vendor=self.invoice.crm, product=self.inv_item.item)
        if len(vendor_items):
            return vendor_items[0]
        else:
            return None
    vendor_item = property(_vendor_item)

    def _price(self):
        if self.vendor_item:
            return self.vendor_item.price
        else:
            return None
    price = property(_price)

    def _value(self):
        if self.price:
            return self.qty * self.price
        else:
            return None
    value = property(_value)

    def _fulfill_qty(self):
        return sum(MyInvoiceReceiveItem.objects.filter(item=self).values_list('qty', flat=True))
    fulfill_qty = property(_fulfill_qty)

    def _fulfill_value(self):
        return sum([x.value for x in MyInvoiceReceiveItem.objects.filter(item=self)])
    fulfill_value = property(_fulfill_value)

    def _fulfill_rate_by_qty(self):
        return self.fulfill_qty * 100.0 / self.qty
    fulfill_rate_by_qty = property(_fulfill_rate_by_qty)

    def _fulfill_rate_by_value(self):
        if self.value:
            return self.fulfill_value * 100.0 / self.value
        else:
            return None
    fulfill_rate_by_value = property(_fulfill_rate_by_value)

    def _qty_balance(self):
        return self.qty - self.fulfill_qty
    qty_balance = property(_qty_balance)

    def _is_editable(self):
        return self.fulfill_qty == 0
    is_editable = property(_is_editable)


class MyInvoiceReceive(models.Model):
    invoice = models.ForeignKey('MyInvoice')
    created_on = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Invoice receive createed by',
        help_text='',
        related_name=u'invoice_receive_loggers'
    )
    reviewed_on = models.DateField(
        null=True,
        blank=True
    )
    reviewed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'Invoice receive reviewed by',
        help_text='',
        related_name=u'invoice_receive_reviewers'
    )

    def __unicode__(self):
        return self.code

    def _code(self):
        return 'INVOICE-RCV%04d' % self.id
    code = property(_code)

    def _qty(self):
        return sum(MyInvoiceReceiveItem.objects.filter(invoice_receive=self).values_list('qty', flat=True))
    qty = property(_qty)

    def _value(self):
        return sum(filter(lambda x: x.value, MyInvoiceReceiveItem.objects.filter(invoice_receive=self)))
    value = property(_value)

    def _is_editable(self):
        return not self.reviewed_by
    is_editable = property(_is_editable)


class MyInvoiceReceiveItem(models.Model):
    invoice_receive = models.ForeignKey('MyInvoiceReceive')
    item = models.ForeignKey('MyInvoiceItem')
    qty = models.PositiveIntegerField(default=1)

    def _value(self):
        if self.item.price:
            return self.qty * self.item.price
        else:
            return None
    value = property(_value)

###################################################
#
#	ShoppingCart models
#
###################################################


class MyShoppingCart(models.Model):
    user = models.ForeignKey(User)
    created_on = models.DateField(auto_now_add=True)
    placed_on = models.DateField(
        null=True,
        blank=True
    )
    is_open = models.BooleanField(default=True)


class MyShoppingCartItem(models.Model):
    cart = models.ForeignKey('MyShoppingCart')
    inv_item = models.ForeignKey('MyItemInventory')
    qty = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0.0)
