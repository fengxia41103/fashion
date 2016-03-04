#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView,CreateView,UpdateView,DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count,Max,Min,Avg
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.template import loader, Context
from django.views.generic.detail import SingleObjectMixin

# django-crispy-forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# django-filters
from django_filters import FilterSet, BooleanFilter,ModelChoiceFilter,AllValuesFilter
from django_filters.views import FilterView
from django_filters.widgets import LinkWidget

# django emails
from django.core.mail import send_mail

# so what
import re,os,os.path,shutil,subprocess, testtools
import random,codecs,unittest,time, tempfile, csv, hashlib
from datetime import datetime as dt
import simplejson as json
from itertools import groupby
import urllib, lxml.html
from utility import MyUtility

from erp.models import *
from erp.forms import *

###################################################
#
#	Common utilities
#
###################################################
def class_view_decorator(function_decorator):
	"""Convert a function based decorator into a class based decorator usable
	on class based Views.
	
	Can't subclass the `View` as it breaks inheritance (super in particular),
	so we monkey-patch instead.
	"""
	
	def simple_decorator(View):
		View.dispatch = method_decorator(function_decorator)(View.dispatch)
		return View
	
	return simple_decorator

###################################################
#
#	Static views
#
###################################################
class HomeView (TemplateView):
	template_name = 'erp/common/home_with_login_modal.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		user_auth_form = AuthenticationForm()
		user_registration_form = UserCreationForm()

		context['registration_form']=user_registration_form
		context['auth_form']=user_auth_form
		return context

###################################################
#
#	User views
#
###################################################
class LoginView(FormView):
	template_name = 'registration/login.html'
	success_url = reverse_lazy('season_list')
	form_class = AuthenticationForm

	def form_valid(self,form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
		    login(self.request, user)
		    return super(LoginView, self).form_valid(form)
		else:
		    return self.form_invalid(form)

class LogoutView(TemplateView):
	template_name = 'registration/logged_out.html'
	def get(self,request):
		logout(request)
    	# Redirect to a success page.
		# messages.add_message(request, messages.INFO, 'Thank you for using our service. Hope to see you soon!')
		return HttpResponseRedirect (reverse_lazy('home'))

class UserRegisterView(FormView):
	template_name = 'registration/register_form.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('login')
	def form_valid(self,form):
		user_name = form.cleaned_data['username']
		password = form.cleaned_data['password2']
		if len(User.objects.filter(username = user_name))>0:
			return self.form_invalid(form)
		else:
			user = User.objects.create_user(user_name, '', password)			
			user.save()

			return super(UserRegisterView,self).form_valid(form)

###################################################
#
#	Attachment views
#
###################################################
@login_required
def attachment_delete_view(request,pk):
	a = Attachment.objects.get(id=pk)
	object_id = a.object_id
	
	# once we set MEDIA_ROOT, we will delete local file from file system also
	if os.path.exists(a.file.path): os.remove(os.path.join(settings.MEDIA_ROOT,a.file.path))
	
	# delete model
	a.delete()
	return HttpResponseRedirect(reverse_lazy('item_detail',kwargs={'pk':object_id}))

def item_attachment_add_view(request, pk):
	tmp_form = AttachmentForm (request.POST, request.FILES)

	if tmp_form.is_valid():
		item = MyItem.objects.get(id=pk)
		t=tmp_form.save(commit=False)

		# file name is random 15 characters
		root,ext = os.path.splitext(request.FILES['file'].name)
		t.name = '%s%s'%(MyUtility().legal_characters(15),ext)

		# description will be item.name by default
		if not t.description: t.description = item.name

		t.content_object = item
		t.created_by = request.user
		t.save()	
	return HttpResponseRedirect(reverse_lazy('item_detail',kwargs={'pk':pk}))

def crm_attachment_add_view(request, pk):
	tmp_form = AttachmentForm (request.POST, request.FILES)

	if tmp_form.is_valid():
		crm = MyCRM.objects.get(id=pk)
		t=tmp_form.save(commit=False)
		
		root,ext = os.path.splitext(request.FILES['file'].name)
		t.name = '%s%s'%(MyUtility().legal_characters(15),ext)
		
		# description will be item.name by default
		if not t.description: t.description = crm.name

		t.content_object = crm
		t.created_by = request.user
		t.save()	
	return HttpResponseRedirect(request.META['HTTP_REFERER'])

###################################################
#
#	MyFiscalYear views
#
###################################################
class MyFiscalYearList(ListView):
	model = MyFiscalYear
	template_name = 'erp/fiscalyear/list.html'
	paginate_by = 10

class MyFiscalYearAdd(CreateView):
	model = MyFiscalYear
	template_name = 'erp/fiscalyear/add.html'
	success_url = reverse_lazy('fiscalyear_list')	
	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = u'New fiscal year'
		context['list_url'] = self.success_url
		context['objects'] = MyFiscalYear.objects.all()
		return context

@class_view_decorator(login_required)
class MyFiscalYearDelete (DeleteView):
	model = MyItem
	template_name = 'erp/common/delete_form.html'
	success_url = reverse_lazy('fiscalyear_list')

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete fiscal year'
		context['list_url'] = reverse_lazy('fiscalyear_list')
		return context	

###################################################
#
#	MyItem views
#
###################################################

class MyItemAdd(CreateView):
	model = MyItem
	template_name = 'erp/common/add_form.html'
	success_url = reverse_lazy('item_list')
	fields = ['brand','season','name','color','price','size_chart']	

	def form_valid(self, form):
		form.instance.created_by = self.request.user

		# force item price in RMB
		currency,created = MyCurrency.objects.get_or_create(abbrev='RMB')
		form.instance.currency = currency
		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = u'New item'
		context['list_url'] = self.success_url
		return context

	def get_success_url(self):
		return reverse_lazy('item_detail', kwargs={'pk':self.object.pk})

@class_view_decorator(login_required)
class MyItemEdit (UpdateView):
	model = MyItem
	template_name = 'erp/common/edit_form.html'
	fields = ['name','description','help_text','season','brand','color','price','size_chart','is_active']

	def get_success_url(self):
		return reverse_lazy('item_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = u'Edit item'
		context['list_url'] = reverse_lazy('item_list')
		return context

@class_view_decorator(login_required)
class MyItemDelete (DeleteView):
	model = MyItem
	template_name = 'erp/common/delete_form.html'
	success_url = reverse_lazy('item_list')

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete item'
		context['list_url'] = reverse_lazy('item_list')
		return context		

class MyItemListFilter (FilterSet):
	brand = ModelChoiceFilter(queryset=MyCRM.objects.vendors().order_by('name'))
	season = ModelChoiceFilter(queryset=MySeason.objects.all().order_by('name'))

	class Meta:
		model = MyItem
		fields = ['brand','season','name']
		together = ['season']

class MyItemList (FilterView):
	template_name = 'erp/item/list.html'
	paginate_by = 25

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'brand': context['filters']['brand'] = MyCRM.objects.get(id=int(val))
				if f == 'season': context['filters']['season'] = MySeason.objects.get(id=int(val))
				if 'name' in f: context['filters']['name__contains'] = val

		# vendors included in queryset
		context['vendors'] = [MyCRM.objects.get(id=v) for v in set(self.object_list.values_list('brand',flat=True))]
		return context		

	def get_filterset_class(self):
		return MyItemListFilter

class MyItemDetail(DetailView):
	model = MyItem
	template_name = 'erp/item/detail.html'

	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)
		context['attachment_form'] = AttachmentForm()
		context['images'] = [img.file.url for img in self.object.attachments.all()]
		context['same_styles'] = MyItem.objects.filter(name=self.object.name,brand=self.object.brand)

		# List all open SO that user can add this item to
		context['sales_orders'] = filter(lambda x: x.is_editable,MySalesOrder.objects.all().order_by('id'))

		# related sales orders
		item_invs = MyItemInventory.objects.filter(item=self.object)
		related_sales_order_ids = set(MySalesOrderLineItem.objects.filter(item__in=item_invs).values_list('order',flat=True))
		context['related_sales_orders'] = MySalesOrder.objects.filter(id__in=related_sales_order_ids)

		# vendor item form
		context['vendor_items'] = MyVendorItem.objects.filter(product=self.object)
		context['vendor_item_form'] = VendorItemAddForm(
			initial={
				'vendor': self.object.brand,
				'currency': self.object.brand.currency,
				'product': self.object,
				'minimal_qty': 1
			}
		)			
		return context

class MyItemListByVendor(TemplateView):
	template_name = 'erp/item/list_by_vendor.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)

		vendor = MyCRM.objects.get(id=int(kwargs['brand']))
		context['brand'] = vendor

		season = MySeason.objects.get(id=int(kwargs['season']))
		context['season'] = season

		# Group item colors under the same item style
		context['items'] = MyItem.objects.filter(brand=vendor,season=season)
		return context

###################################################
#
#	MyCRM views
#
###################################################

class MyVendorList(ListView):
	model = MyCRM
	template_name = 'erp/crm/vendor_list.html'

	def get_queryset(self):
		return MyCRM.objects.vendors()

class MyVendorAdd(CreateView):
	model = MyCRM
	template_name = 'erp/common/add_form.html'
	success_url = reverse_lazy('vendor_list')
	fields = ['name','description','contact','phone','currency']

	def form_valid(self, form):
		form.instance.crm_type = 'V'
		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = u'New Vendor'
		context['list_url'] = self.success_url
		context['objects'] = MyCRM.objects.all()
		return context

@class_view_decorator(login_required)
class MyVendorEdit (UpdateView):
	model = MyCRM
	template_name = 'erp/common/edit_form.html'
	success_url = reverse_lazy('vendor_list')
				
	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = u'Edit Vendor'
		context['list_url'] = reverse_lazy('vendor_list')
		context['attachment_form'] = AttachmentForm()
		return context		

class MyVendorDetail(DetailView):
	model = MyCRM
	template_name = 'erp/crm/vendor_detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		seasons = MyItem.objects.filter(brand=self.object).values_list('season',flat=True)

		tmp = {}
		for season in MySeason.objects.filter(id__in = seasons).order_by('name'):
			items = MyItem.objects.filter(brand=self.object,season=season)
			samples = reduce(lambda x,y:x+y,[list(item.attachments.all()) for item in items])
			tmp[season] = samples
		context['seasons'] = tmp
		return context

class MyCustomerList(ListView):
	model = MyCRM
	template_name = 'erp/crm/customer_list.html'

	def get_queryset(self):
		return MyCRM.objects.customers()

class MyCustomerAdd(CreateView):
	model = MyCRM
	template_name = 'erp/common/add_form.html'
	success_url = reverse_lazy('customer_list')
	fields = ['name','description','contact','phone','currency','std_discount']

	def form_valid(self, form):
		form.instance.crm_type = 'C'
		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = u'New Customer'
		context['list_url'] = self.success_url
		context['objects'] = MyCRM.objects.all()
		return context

@class_view_decorator(login_required)
class MyCustomerEdit (UpdateView):
	model = MyCRM
	template_name = 'erp/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('customer_list', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = u'Edit Customer'
		context['list_url'] = reverse_lazy('customer_list')
		return context		

###################################################
#
#	MyItemInventory views
#
###################################################
def add_to_inventory(storage,quick_notion,out,reason,created_by):
	errors = {}	
	
	# Set "withdrawable" flag. Customer inventory is used to
	# track how many items we have ever shipped to them, so they are not drawable.
	if storage.location.crm.crm_type == 'C': withdrawable = False
	else: withdrawable = True

	# Parse items
	items = []
	pat = re.compile("(?P<size>\D+)-?(?P<qty>\d+)")	
	for line_no, line in enumerate(quick_notion.split('\n')):
		tmp = line.split(',')
		sku = tmp[0]

		# Find MyItem object
		tmp_items = MyItem.objects.filter(id=int(sku))
		if len(tmp_items) == 0: 
			errors[line_no+1]={'line':line,'reason':'not found'}
			continue
		elif len(tmp_items) > 1:
			errors[line_no+1] = {'line':line,'reason':'multiple matches'}
			continue
		item = tmp_items[0]
		items.append(item)

		# Adjust inventory
		for (size,qty) in pat.findall(','.join(tmp[1:])):
			# Get MyItemInventory obj
			item_inv, created = MyItemInventory.objects.get_or_create(
				item = item,
				size = size.upper(),
				storage = storage,
				withdrawable = withdrawable
			)

			# Create MyItemInventoryAudit
			audit = MyItemInventoryMoveAudit(
				created_by = created_by,
				inv = item_inv,
				out = False, # We are adding to inventory
				qty = qty,
				reason = reason,
			).save()

	return {'errors':errors, 'items':items}

class MyItemInventoryAdd(FormView):
	template_name = 'erp/item/inv_add.html'
	form_class = ItemInventoryAddForm
	success_url = '#'

	def form_valid(self, form):
		messages.info(
            self.request,
            "Items have been added to inventory"
        )		

		# Call utility function to parse
		result = add_to_inventory(
			form.cleaned_data['storage'], # storyage
			form.cleaned_data['items'].strip(), # input shorhand notion
			False, # add to inventory
			form.cleaned_data['reason'], # reason for this adjustment
			self.request.user, # created by user
		)

		return super(FormView, self).form_valid(form)

###################################################
#
#	MySeason views
#
###################################################		

class MySeasonList(ListView):
	model = MySeason
	template_name = 'erp/season/list.html'

	def get_queryset(self):
		return MySeason.objects.all().order_by('-name')

class MySeasonDetail(DetailView):
	model = MySeason
	template_name = 'erp/season/detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		vendors = set(MyItem.objects.filter(season=self.object).values_list('brand',flat=True))
		
		# Get vendor stats
		vendor_stats = []
		for v in [MyCRM.objects.get(id=int(v)) for v in vendors]:
			num_of_items = MyItem.objects.filter(season=self.object,brand=v).count()
			vendor_stats.append((v,num_of_items))
		context['vendors'] = vendor_stats

		# Attachment for to upload vendor images
		# TODO: auto download from Pinterest.
		context['attachment_form'] = AttachmentForm()

		# Other seasons
		return context

###################################################
#
#	MyBusinessModel views
#
###################################################
class MyBusinessModelAdd(CreateView):
	model = MyBusinessModel
	template_name = 'erp/common/add_form.html'
	fields = ['name','description','abbrev','sales_model']

###################################################
#
#	Sales Order views
#
###################################################

def add_item_to_sales_order(quick_notion,so):
	errors = {}	

	# Parse items
	items = []
	pat = re.compile("(?P<size>\D+)-?(?P<qty>\d+)")
	for line_no, line in enumerate(quick_notion.split('\n')):
		tmp = line.split(',')
		sku = tmp[0]

		# Find MyItem object
		tmp_items = MyItem.objects.filter(id=int(sku))
		if len(tmp_items) == 0: 
			errors[line_no+1]={'line':line,'reason':'not found'}
			continue
		elif len(tmp_items) > 1:
			errors[line_no+1] = {'line':line,'reason':'multiple matches'}
			continue
		item = tmp_items[0]
		items.append(item)

		# Create order
		for (size,qty) in pat.findall(','.join(tmp[1:])):
			# Get MyItemInventory obj
			item_inv, created = MyItemInventory.objects.get_or_create(
				item = item,
				size = size.upper(),
				storage = so.default_storage,
				item_type = 'New' # we are filling ORDER using New items
			)

			# Create SO line item
			if so.is_sold_at_cost: price = item.converted_cost
			else: price = item.price

			existing = MySalesOrderLineItem.objects.filter(order=so,item=item_inv)
			if len(existing) and not existing[0].fullfill_qty > 0: 
				# only modifiable when there has not been any fullfillment yet to this item
				existing[0].qty += int(qty)
				existing[0].save()
			else:
				line_item = MySalesOrderLineItem(
					order = so,
					item = item_inv,
					price = price,
					qty = int(qty)
				).save()

	return {'errors':errors, 'items':items}

class MySalesOrderAdd(FormView):
	template_name = 'erp/so/add.html'
	form_class = SalesOrderAddForm
	order = None

	def get_success_url(self):
		if self.order: return reverse_lazy('so_detail',kwargs={'pk':self.order.id})
		else: return reverse_lazy('so_list')

	def form_valid(self, form):
		messages.info(
            self.request,
            "Your sales order has been created."
        )		

		# Create sales order
		so = form.save(commit=False)
		so.created_by = self.request.user
		if form.cleaned_data['discount']: so.discount = form.cleaned_data['discount']
		else: so.discount = so.customer.std_discount

		so.save()
		self.order = so

		# Add item to SO
		result = add_item_to_sales_order(form.cleaned_data['items'],so)

		return super(FormView, self).form_valid(form)

class MySalesOrderEdit(UpdateView):
	model = MySalesOrder

	def get_success_url(self):
		 return reverse_lazy('so_detail', kwargs={'pk': self.object.id})

class MySalesOrderListFilter (FilterSet):
	customer = ModelChoiceFilter(queryset=MyCRM.objects.filter(crm_type='C').order_by('name'))
	class Meta:
		model = MySalesOrder
		fields = {
			'customer':['exact'],
			'sales':['exact'],
		}

class MySalesOrderList (FilterView):
	template_name = 'erp/so/list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MySalesOrderListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'customer': context['filters']['customer'] = MyCRM.objects.get(id=int(val))
				if f == 'sales': context['filters']['sales'] = User.objects.get(id=int(val))
		return context

class MySalesOrderDelete(DeleteView):
	model = MySalesOrder
	success_url = reverse_lazy('so_list')

class MySalesOrderDetail(DetailView):
	model = MySalesOrder
	template_name = 'erp/so/detail.html'

	def get_context_data(self, **kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		line_items = MySalesOrderLineItem.objects.filter(order = self.object)

		# Group same item sizes
		items = {}
		for i in line_items:
			item = i.item.item

			# Get vendor
			brand = item.brand
			if brand not in items: items[brand] = {'total_qty':0,'total_value':0, 'items':{}}
			items[brand]['total_qty'] += i.qty
			items[brand]['total_value'] += i.discount_value

			# Get item
			if item not in items[brand]['items']: items[brand]['items'][item] = {'so_line_items':[],'qty':0,'value':0}

			# Get size and qty
			items[brand]['items'][item]['so_line_items'].append(i)
			items[brand]['items'][item]['qty'] += i.qty
			items[brand]['items'][item]['value'] += i.discount_value
		context['items'] = items

		# SO edit view
		context['so_edit_form'] = SalesOrderEditForm(instance=self.object)

		# SO payment add view
		context['so_payment_add_form'] = SalesOrderPaymentAddForm(initial={
			'so':self.object,
			'amount':self.object.account_receivable
		})

		return context

class MySalesOrderAddItem(TemplateView):
	template_name = ''

	def post(self,request):
		so = int(request.POST['so'])
		item_inv = request.POST['item-inv'].replace(',','')
		qty = int(request.POST['qty'])

		MySalesOrder.objects.get(id=so)
		item_inv = MyItemInventory.objects.get(id=int(item_inv))

		if so.is_sold_at_cost: price = item_inv.item.converted_cost
		else: price = item_inv.item.price

		# Create line item
		line_item,created = MySalesOrderLineItem.objects.get_or_create(
				order = so,
				item = item_inv
		)
		if created: line_item.price = price
		line_item.qty += qty
		line_item.save()

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')		

class MySalesOrderLineItemDelete(DeleteView):
	model = MySalesOrderLineItem
	template_name = 'erp/so/remove_item.html'

	def get_success_url(self):
		return reverse_lazy('so_detail',kwargs={'pk':self.object.order.id})

	def get_context_data(self,**kwargs):
		context = super(DeleteView,self).get_context_data(**kwargs)
		context['cancel_redirect_url'] = self.get_success_url()
		return context

###################################################
#
#	Sales Order Payment views
#
###################################################
class MySalesOrderPaymentList(ListView):
	model = MySalesOrderPayment
	template_name = 'erp/payment/payment/so_list.html'

class MySalesOrderPaymentAdd(FormView):
	form_class = SalesOrderPaymentAddForm
	payment = None

	def get_success_url(self):
		if self.payment: return reverse_lazy('so_detail',kwargs={'pk':self.payment.so.id})
		else: return reverse_lazy('so_payment_list')

	def form_valid(self,form):
		payment = form.save(commit=False)
		payment.created_by = self.request.user
		payment.save()
		self.payment = payment
		return super(FormView, self).form_valid(form)		

###################################################
#
#	Sales Order Fullfillment views
#
###################################################

@class_view_decorator(login_required)
class MySalesOrderFullfillmentAdd(DetailView):
	model = MySalesOrder
	template_name = 'erp/so/fullfill_add.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)

		items = {}
		for line_item in MySalesOrderLineItem.objects.filter(order=self.object).order_by('item__id'):
			if line_item.qty_balance > 0: 
				brand = line_item.item.item.brand
				if brand not in items: items[brand] = []
				items[brand].append(line_item)
		context['items'] = items
		return context

	def post(self,request,pk):
		'''
		Post to this API will create a sales order fullfillment.
		'''
		items = []
		for line_id,qty in self.request.POST.iteritems():
			if 'line-item' in line_id and int(qty):
				line_item = MySalesOrderLineItem.objects.get(id=int(line_id.split('-')[-1]))
				items.append((line_item,qty))

		if len(items):
			# Create MySalesOrderFullfillment
			fullfill = MySalesOrderFullfillment(
				so=items[0][0].order,
				created_by = self.request.user
			)
			fullfill.save()

			# Add fullfill items to MySalesOrderFullfillment
			for so_line_item,qty in items:
				MySalesOrderFullfillmentLineItem(
					so_fullfillment = fullfill,
					so_line_item = so_line_item,
					fullfill_qty = int(qty)
				).save()
		return HttpResponseRedirect(reverse_lazy('so_fullfill_detail',kwargs={'pk':fullfill.id}))

class MySalesOrderFullfillmentDetail(DetailView):
	model = MySalesOrderFullfillment
	template_name = 'erp/so/fullfill_detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)

		items = {}
		for line_item in MySalesOrderFullfillmentLineItem.objects.filter(so_fullfillment=self.object).order_by('so_line_item__id'):
			brand = line_item.so_line_item.item.item.brand
			if brand not in items: items[brand] = []
			items[brand].append(line_item)
		context['items'] = items
		return context

@class_view_decorator(login_required)
class MySalesOrderFullfillmentEdit(UpdateView):
	model = MySalesOrderFullfillment

	def post(self,request,pk):
		items = []
		for line_id,qty in self.request.POST.iteritems():
			if 'line-item-fullfill' in line_id:
				qty = int(qty)		
				f = MySalesOrderFullfillmentLineItem.objects.get(id=int(line_id.split('-')[-1]))			
				if qty and qty != f.fullfill_qty: 
					f.fullfill_qty = qty
					f.save() # update FullfillLineItem qty
				elif qty == 0: # equal to delete this line item
					f.delete()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MySalesOrderFullfillmentDelete(DeleteView):
	model = MySalesOrderFullfillment
	template_name = 'erp/common/delete_form.html'

	def get_success_url(self):
		return reverse_lazy('so_detail',kwargs={'pk':self.object.so.id})

@class_view_decorator(login_required)
class MySalesOrderFullfillmentReview(TemplateView):
	'''
	Finalize a SO fullfillment. Once finalized, the fullfillment will not be editable.
	'''
	def post(self,request,pk):
		fullfill = MySalesOrderFullfillment.objects.get(id=int(pk))
		fullfill.reviewed_by = self.request.user
		fullfill.reviewed_on = dt.now()
		fullfill.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MySalesOrderFullfillmentReviewBatch(TemplateView):
	'''
	Batch finalize all fullfillments that are linked to a SO.
	'''
	def post(self,request,pk):
		so = MySalesOrder.objects.get(id=int(pk))
		for fullfill in MySalesOrderFullfillment.objects.filter(so=so):
			if not fullfill.is_editable: continue
			
			fullfill.reviewed_by = self.request.user
			fullfill.reviewed_on = dt.now()
			fullfill.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

###################################################
#
#	Sales Order Return views
#
###################################################

class MySalesOrderReturnAdd(DetailView):
	model = MySalesOrder
	template_name = 'erp/so/return_add.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)

		items = {}
		for line_item in MySalesOrderLineItem.objects.filter(order=self.object).order_by('item__id'):
			if line_item.fullfill_qty > 0: 
				brand = line_item.item.item.brand
				if brand not in items: items[brand] = []
				items[brand].append(line_item)
		context['items'] = items
		context['reasons'] = MyReturnReason.objects.all()
		return context

	def post(self,request,pk):
		'''
		Post to this API will create a sales order fullfillment.
		'''
		items = {}
		for line_id,val in self.request.POST.iteritems():
			if 'line-item' in line_id and int(val):
				line_item = MySalesOrderLineItem.objects.get(id=int(line_id.split('-')[-1]))
				items[line_item.id] = {'item':line_item,'qty':int(val)}
		for line_id,val in self.request.POST.iteritems():				
			if 'reason' in line_id:
				line_item_id = int(line_id.split('-')[-1])
				if line_item_id in items:
					return_reason = MyReturnReason.objects.get(id=int(val))
					items[line_item_id]['reason'] = return_reason

		if len(items):
			so = MySalesOrder.objects.get(id=pk)

			# Create MySalesOrderFullfillment
			so_return = MySalesOrderReturn(
				so=so,
				created_by = self.request.user
			)
			so_return.save()

			# Add return items to MySalesOrderReturn
			for so_line_item_id,data in items.iteritems():
				MySalesOrderReturnLineItem(
					so_return = so_return,
					so_line_item = data['item'],
					return_qty = data['qty'],
					reason = data['reason']
				).save()
			
		return HttpResponseRedirect(reverse_lazy('so_return_detail',kwargs={'pk':so_return.id}))

class MySalesOrderReturnDetail(DetailView):
	model = MySalesOrderReturn
	template_name = 'erp/so/return_detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)

		items = {}
		for line_item in MySalesOrderReturnLineItem.objects.filter(so_return=self.object).order_by('so_line_item__id'):
			brand = line_item.so_line_item.item.item.brand
			if brand not in items: items[brand] = []
			items[brand].append(line_item)
		context['items'] = items
		context['reasons'] = MyReturnReason.objects.all()

		return context

class MySalesOrderReturnEdit(UpdateView):
	model = MySalesOrderReturn

	def post(self,request,pk):
		items = {}
		for line_id,val in self.request.POST.iteritems():
			if 'line-item' in line_id and int(val):
				line_item = MySalesOrderReturnLineItem.objects.get(id=int(line_id.split('-')[-1]))
				line_item.return_qty = int(val)
				line_item.save()
			elif 'reason' in line_id and int(val):
				line_item = MySalesOrderReturnLineItem.objects.get(id=int(line_id.split('-')[-1]))
				line_item.reason = MyReturnReason.objects.get(id=int(val))
				line_item.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])	

@class_view_decorator(login_required)
class MySalesOrderReturnDelete(DeleteView):
	model = MySalesOrderReturn
	template_name = 'erp/common/delete_form.html'

	def get_success_url(self):
		return reverse_lazy('so_detail',kwargs={'pk':self.object.so.id})

@class_view_decorator(login_required)
class MySalesOrderReturnReview(TemplateView):
	def post(self,request,pk):
		so_return = MySalesOrderReturn.objects.get(id=int(pk))
		so_return.reviewed_by = self.request.user
		so_return.reviewed_on = dt.now()
		so_return.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MySalesOrderReturnReviewBatch(TemplateView):
	'''
	Batch finalize all returns that are linked to a SO.
	'''
	def post(self,request,pk):
		so = MySalesOrder.objects.get(id=int(pk))
		for so_return in MySalesOrderReturn.objects.filter(so=so):
			if not so_return.is_editable: continue
			
			so_return.reviewed_by = self.request.user
			so_return.reviewed_on = dt.now()
			so_return.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MySalesOrderReturnReviewUndo(TemplateView):
	def post(self,request,pk):
		so_return = MySalesOrderReturn.objects.get(id=int(pk))
		so_return.reviewed_by = None
		so_return.reviewed_on = None
		so_return.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

###################################################
#
#	MyVendorItem views
#
###################################################

class MyVendorItemAdd(FormView):
	form_class = VendorItemAddForm
	vendor_item = None
	def form_valid(self, form):
		messages.info(
            self.request,
            "Your vendor item has been created."
        )		

		# Create sales order
		self.vendor_item = form.save()
		return super(FormView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('item_detail', kwargs={'pk':self.vendor_item.product.pk})

class MyVendorItemDelete(DeleteView):
	model = MyVendorItem
	template_name = 'erp/common/delete_form.html'

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete vendor item'
		context['list_url'] = reverse_lazy('vendor_item_list')
		context['cancel_redirect_url'] = self.get_success_url()
		return context	

	def get_success_url(self):
		return reverse_lazy('item_detail', kwargs={'pk':self.object.product.pk})

class MyVendorItemListFilter (FilterSet):
	class Meta:
		model = MyVendorItem
		fields = {
			'sku':['contains'],
			'vendor':['exact'],
			'order_deadline':['lte']
		}

class MyVendorItemList (FilterView):
	template_name = 'erp/item/vendor_item_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MyVendorItemListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'vendor': context['filters']['vendor'] = MyCRM.objects.get(id=int(val))
				if f == 'currency': context['filters']['currency'] = MyCurrency.objects.get(id=int(val))
				if f == 'product': context['filters']['item'] = MyItem.objects.get(id=int(val))

		return context

class MyVendorItemEdit(UpdateView):
	model = MyVendorItem
	template_name = 'erp/common/edit_form.html'
	class Meta:
		exclude = ('product','vendor','currency')