#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms import formset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView,CreateView,UpdateView,DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count,Max,Min,Avg
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files import File                                         
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

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
from tempfile import NamedTemporaryFile
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
class HomeView(TemplateView):
	template_name = 'erp/common/home.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['contact_form'] = ContactForm()
		return context	

###################################################
#
#	User views
#
###################################################
class LoginView(FormView):
	template_name = 'registration/login.html'
	success_url = reverse_lazy('location_list')
	form_class = AuthenticationForm

	def form_valid(self,form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
		    login(self.request, user)
		    return HttpResponseRedirect(reverse_lazy('location_list'))
		else:
		    return self.form_invalid(form)

class LogoutView(TemplateView):
	template_name = 'registration/logged_out.html'
	def get(self,request):
		logout(request)
		return HttpResponseRedirect (reverse_lazy('home'))

class UserRegisterView(FormView):
	template_name = 'registration/registration.html'
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

			# login after
			login(self.request, user)
			return HttpResponseRedirect(reverse_lazy('location_list'))

@class_view_decorator(csrf_exempt)
class APILogin(TemplateView):
	def post(self,request):
		data = json.loads(request.body)
		username = data['username']
		password = data['password']
		user = authenticate(username=username, password=password)

		print 'here', username, password

		if user is not None and user.is_active:
		    login(self.request, user)
		    return HttpResponse(json.dumps({'apikey':user.api_key.key}), 
			content_type='application/javascript')
		else:
		    return HttpResponse(json.dumps({'status':'403','error':'user not found'}), 
			content_type='application/javascript')

@class_view_decorator(csrf_exempt)
class APILogout(TemplateView):
	def post(self,request):
		logout(request)
		return HttpResponse(json.dumps({'data':'bye'}), 
			content_type='application/javascript')

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

@login_required
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

@login_required
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
		fields = {
			'brand':['exact'],
			'season':['exact'],
			'name':['icontains']
		}
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
				if 'name' in f: context['filters']['name__icontains'] = val

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
		context['related_sales_orders'] = MySalesOrderLineItem.objects.filter(item__in=item_invs)

		# related purchase orders
		item_invs = MyItemInventory.objects.filter(item=self.object)
		context['related_purchase_orders'] = MyPurchaseOrderLineItem.objects.filter(inv_item__in=item_invs)


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

from zipfile import ZipFile
class MyItemImageBatchUpload(TemplateView):
	template_name = 'erp/item/image_batch_upload.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['form'] = ItemImageBatchUploadForm()
		return context

	def post(self,request):
		form = ItemImageBatchUploadForm(request.POST, request.FILES)
		errors = []

		if form.is_valid():
			season = form.cleaned_data['season']
			vendor = form.cleaned_data['vendor']
			my_zip = ZipFile(request.FILES['images'])
			for member in my_zip.namelist():
				head,file_name = os.path.split(member)
				if not file_name: continue # if empty, skip

				style,ext = os.path.splitext(file_name)
				if '&' not in style:
					errors.append((member,'Format error. "&" not found.'))
					continue

				tmp = style.split('&')
				if len(tmp) < 2:
					errors.append((member,'Format error. Should be "style&color[&index].jpg[|png]."'))
					continue

				style = tmp[0].replace(',','/').strip()
				color = tmp[1].strip()
				print style, color

				items = MyItem.objects.filter(name__iexact=style,color__iexact=color,brand=vendor,season=season)
				if not len(items):
					errors.append((member,'Item not found'))
					continue

				# unzip file to a tmp file
				data = my_zip.read(member)
				prefix = MyUtility().legal_characters(9)
				tmp_file = NamedTemporaryFile(prefix=prefix,suffix=ext,delete=True)
				tmp_file.write(data)

				# save image as attachment to item
				for item in items:
					Attachment(
						name = os.path.split(tmp_file.name)[1],
						description = item.name,
						content_object = item,
						created_by = request.user,
						file = File(tmp_file)
					).save()
				tmp_file.close()

			if len(errors):
				return render(request, self.template_name, {'form':form,'errors':errors})     			
			else:
				return HttpResponseRedirect(reverse_lazy('item_list_by_vendor',kwargs={'season':season.id,'brand':vendor.id}))
		else: 
			return render(request, self.template_name, {'form':form})     

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
			audit = MyItemInventoryTheoreticalAudit(
				created_by = created_by,
				inv = item_inv,
				out = False, # We are adding to inventory
				qty = qty,
				reason = reason,
			).save()

	return {'errors':errors, 'items':items}

class MyItemInventoryAdd(FormView):
	template_name = 'erp/inv/initial_add.html'
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

class MyItemInventoryPhysicalAdd(TemplateView):
	template_name = 'erp/inv/physical_add.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		storage = MyStorage.objects.get(id = int(kwargs['storage']))
		context['vendor'] = vendor = MyCRM.objects.get(id = int(kwargs['vendor']))
		context['season'] = season = MySeason.objects.get(id = int(kwargs['season']))

		context['storage'] = storage
		context['storages'] = MyStorage.objects.exclude(id=storage.id)
		context['inv_items'] = MyItemInventory.objects.filter(storage=storage,item__brand=vendor,item__season=season).order_by('item__name')
		return context

	def post(self,request,storage,vendor):
		# print request.POST
		items = {}
		for line_id,val in self.request.POST.iteritems():
			if 'inv-item' in line_id :
				inv_item = MyItemInventory.objects.get(id=int(line_id.split('-')[-1]))

				# we are listing "0"s, but they are not saved unless the "on" is set to TRUE
				# they are set to FALSE by default.
				items[inv_item.id] = {'item':inv_item,'qty':int(val),'on':False}
		for line_id,val in self.request.POST.iteritems():				
			if 'set-zero' in line_id:
				line_item_id = int(line_id.split('-')[-1])
				if line_item_id in items:
					items[line_item_id]['on'] = True

		for inv_item_id,data in items.iteritems():
			if data['qty'] or data['on']:
				MyItemInventoryPhysicalAudit(
					created_by = request.user,
					inv = data['item'],
					physical = data['qty'],
					theoretical = data['item'].theoretical
				).save()

		return HttpResponseRedirect(request.META['HTTP_REFERER'])

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
		elif not tmp_items[0].is_so_ready:
			errors[line_no+1] = {'line':line,'reason':'not SO ready'}

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
	customer = ModelChoiceFilter(queryset=MyCRM.objects.customers())
	class Meta:
		model = MySalesOrder
		fields = {
			'customer':['exact'],
			'sales':['exact'],
			'business_model':['exact']
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

		# Group same item sizes
		items = {}
		for i in MySalesOrderLineItem.objects.filter(order = self.object):
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
		if self.object.account_receivable:
			context['so_payment_add_form'] = SalesOrderPaymentAddForm(initial={
				'so':self.object,
				'amount':self.object.account_receivable
			})
		else:
			context['so_payment_add_form'] = SalesOrderPaymentAddForm(initial={
				'so':self.object,
				'usage':'deposit', # we default to deposit if there is no AR
				'amount':1.0
			})			

		# related POs
		context['purchase_orders'] = MyPurchaseOrder.objects.filter(so=self.object)

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

@class_view_decorator(login_required)
class MySalesOrderLineItemUpdateQty(TemplateView):
	def post(self,request):
		id = int(request.POST['id'].split('-')[-1])
		item = MySalesOrderLineItem.objects.get(id=id)
		item.qty = request.POST['val']
		item.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

class MySalesOrderToPurchaseOrder(TemplateView):
	'''
	Convert sales orders to POs
	'''
	def post(self,request,pk):
		so = MySalesOrder.objects.get(id=int(pk))

		items_by_brand = {}
		for i in MySalesOrderLineItem.objects.filter(order = so):
			item = i.item.item
			if item.brand not in items_by_brand: items_by_brand[item.brand] = []
			items_by_brand[item.brand].append(i)

		for brand,items in items_by_brand.iteritems():
			po = MyPurchaseOrder(
				so = so,
				vendor = brand,
				location = so.default_storage.location,
				created_by = request.user
			)
			po.save()

			for item in items:
				po_line_item = MyPurchaseOrderLineItem(
					po = po,
					inv_item = item.item,
					qty = item.qty,
				).save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])


###################################################
#
#	Sales Order Payment views
#
###################################################
class MySalesOrderPaymentListFilter (FilterSet):
	class Meta:
		model = MySalesOrderPayment
		fields = {
			'so':['exact'],
			'payment_method':['exact'],
		}

class MySalesOrderPaymentList (FilterView):
	template_name = 'erp/payment/so_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MySalesOrderPaymentListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'so': context['filters']['so'] = MySalesOrder.objects.get(id=int(val))
		return context

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

@class_view_decorator(login_required)
class MySalesOrderPaymentReview(TemplateView):
	'''
	Finalize a SO payment. Once finalized, the payment will not be editable.
	'''
	def post(self,request,pk):
		payment = MySalesOrderPayment.objects.get(id=int(pk))
		payment.reviewed_by = self.request.user
		payment.reviewed_on = dt.now()
		payment.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MySalesOrderPaymentDelete(DeleteView):
	model = MySalesOrderPayment
	template_name = 'erp/common/delete_form.html'

	def get_success_url(self):
		return reverse_lazy('so_detail',kwargs={'pk':self.object.so.id})

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

class MySalesOrderFullfillmentListFilter (FilterSet):
	class Meta:
		model = MySalesOrderFullfillment
		fields = {
			'so':['exact'],
		}

class MySalesOrderFullfillmentList (FilterView):
	template_name = 'erp/so/fullfill_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MySalesOrderFullfillmentListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'so': context['filters']['so'] = MySalesOrder.objects.get(id=int(val))
		return context

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
		else:
			return HttpResponseRedirect(reverse_lazy('so_detail',kwargs={'pk':pk}))

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

class MySalesOrderReturnListFilter (FilterSet):
	class Meta:
		model = MySalesOrderReturn
		fields = {
			'so':['exact'],
		}

class MySalesOrderReturnList (FilterView):
	template_name = 'erp/so/return_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MySalesOrderReturnListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'so': context['filters']['so'] = MySalesOrder.objects.get(id=int(val))
		return context

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

###################################################
#
#	MyPurchaseOrder views
#
###################################################
def add_item_to_purchase_order(quick_notion,po):
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
		elif not tmp_items[0].is_po_ready:
			errors[line_no+1] = {'line':line,'reason':'not PO ready'}
			continue			
		item = tmp_items[0]
		items.append(item)

		# Create order
		for (size,qty) in pat.findall(','.join(tmp[1:])):
			# Get MyItemInventory obj
			item_inv, created = MyItemInventory.objects.get_or_create(
				item = item,
				size = size.upper(),
				storage = po.location.primary_storage,
				item_type = 'New' # we are purchasing New items ONLY!
			)

			existing = MyPurchaseOrderLineItem.objects.filter(po=po,inv_item=item_inv)
			if len(existing) and not existing[0].fullfill_qty > 0: 
				# only modifiable when there has not been any fullfillment yet to this item
				existing[0].qty += int(qty)
				existing[0].save()
			else:
				line_item = MyPurchaseOrderLineItem(
					po = po,
					inv_item = item_inv,
					qty = int(qty)
				).save()

	return {'errors':errors, 'items':items}

class MyPurchaseOrderAdd(FormView):
	template_name = 'erp/po/add.html'
	form_class = PurchaseOrderAddForm
	order = None

	def get_success_url(self):
		if self.order: return reverse_lazy('po_detail',kwargs={'pk':self.order.id})
		else: return reverse_lazy('po_list')

	def form_valid(self, form):
		messages.info(
            self.request,
            "Your sales order has been created."
        )		

		# Create sales order
		po = form.save(commit=False)
		po.created_by = self.request.user
		po.save()
		self.order = po

		# Add item to SO
		result = add_item_to_purchase_order(form.cleaned_data['items'],po)
		return super(FormView, self).form_valid(form)

class MyPurchaseOrderListFilter (FilterSet):
	vendor = ModelChoiceFilter(queryset=MyCRM.objects.vendors())
	class Meta:
		model = MyPurchaseOrder
		fields = {
			'vendor':['exact'],
			'so':['exact'],
		}

class MyPurchaseOrderList (FilterView):
	template_name = 'erp/po/list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MyPurchaseOrderListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'vendor': context['filters']['vendor'] = MyCRM.objects.get(id=int(val))
				if f == 'so': context['filters']['so'] = MySalesOrder.objects.get(id=int(val))
		return context

class MyPurchaseOrderDetail(DetailView):
	model = MyPurchaseOrder
	template_name = 'erp/po/detail.html'

	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)
		context['months'] = ESTIMATED_MONTH_CHOICES
		context['fullfillments'] = MyPOFullfillment.objects.filter(po=self.object)
		return context

class MyPurchaseOrderDelete(DeleteView):
	model = MyPurchaseOrder
	template_name = 'erp/common/delete_form.html'	
	success_url = reverse_lazy('po_list')

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete Purchase Order'
		context['list_url'] = reverse_lazy('po_list')
		return context

@class_view_decorator(login_required)
class MyPurchaseOrderPlace(TemplateView):
	def post(self,request,pk):
		po = MyPurchaseOrder.objects.get(id=int(pk))

		# TODO: send order to vendor via email

		# Save time stamp
		po.placed_on = dt.now()
		po.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyPurchaseOrderLineItemUpdateAvailability(TemplateView):
	def post(self,request):
		id = int(request.POST['id'].split('-')[-1])
		item = MyPurchaseOrderLineItem.objects.get(id=id)
		item.available_in = request.POST['val']
		item.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

###################################################
#
#	MyInvoice views
#
###################################################
@class_view_decorator(login_required)
class MyVendorInvoiceAdd(TemplateView):
	template_name = 'erp/invoice/vendor_add.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		# get vendor items
		context['vendor'] = vendor = MyCRM.objects.get(id=int(kwargs['pk']))

		# form
		context['form'] = VendorInvoiceAddForm(initial={
			'crm':vendor,
			'created_by':self.request.user
		})

		# get open items
		items = {}
		for item in MyPurchaseOrderLineItem.objects.filter(po__vendor=vendor).order_by('inv_item__item__name'):
			if item not in items: items[item.inv_item] = 0
			items[item.inv_item] += item.qty
		context['items'] = items

		return context

	def post(self,request,pk):
		# create invoice
		form = VendorInvoiceAddForm(self.request.POST)
		if form.is_valid():
			# create invoice
			invoice = form.save()

			# create invoice item records
			for line_id,val in self.request.POST.iteritems():
				if 'inv-item' in line_id and int(val):
					inv_item = MyItemInventory.objects.get(id=int(line_id.split('-')[-1]))
					MyInvoiceItem(
						invoice = invoice,
						inv_item = inv_item,
						qty = int(val)
					).save()
	        return HttpResponseRedirect(reverse_lazy('invoice_detail',kwargs={'pk':invoice.id}))
		# else:
		# 	return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyInvoiceDetail(DetailView):
	model = MyInvoice
	template_name = 'erp/invoice/detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		context['items'] = MyInvoiceItem.objects.filter(invoice=self.object)
		
		# Invoice edit view
		context['invoice_edit_form'] = VendorInvoiceAddForm(instance=self.object)		
		return context

@class_view_decorator(login_required)
class MyInvoiceDelete(DeleteView):
	model = MyInvoice
	template_name = 'erp/common/delete_form.html'	
	success_url = reverse_lazy('invoice_list')

class MyInvoiceEdit(UpdateView):
	model = MyInvoice

	def get_success_url(self):
		 return reverse_lazy('invoice_detail', kwargs={'pk': self.object.id})

class MyInvoiceLineItemEdit(UpdateView):
	model = MyInvoice

	def post(self,request,pk):
		items = {}
		for line_id,val in self.request.POST.iteritems():
			if 'invoice-item' in line_id and int(val):
				line_item = MyInvoiceItem.objects.get(id=int(line_id.split('-')[-1]))
				line_item.qty = int(val)
				line_item.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyInvoiceReview(TemplateView):
	def post(self,request,pk):
		invoice = MyInvoice.objects.get(id=int(pk))
		invoice.reviewed_by = self.request.user
		invoice.reviewed_on = dt.now()
		invoice.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])	

class MyInvoiceListFilter (FilterSet):
	crm = ModelChoiceFilter(queryset=MyCRM.objects.vendors())
	class Meta:
		model = MyInvoice
		fields = {
			'crm':['exact'],
			'invoice_no':['contains'],
		}

class MyInvoiceList (FilterView):
	template_name = 'erp/invoice/list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MyInvoiceListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'crm': context['filters']['crm'] = MyCRM.objects.get(id=int(val))
		return context

@class_view_decorator(login_required)
class MyInvoiceReceiveAdd(DetailView):
	model = MyInvoice
	template_name = 'erp/invoice/receive_add.html'
	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)

		# get open items
		context['items'] = filter(lambda x: x.qty_balance>0, MyInvoiceItem.objects.filter(invoice=self.object))

		return context

	def post(self,request,pk):
		invoice = MyInvoice.objects.get(id=int(pk))
		invoice_receive = MyInvoiceReceive(
			invoice = invoice,
			created_by = self.request.user
		)
		invoice_receive.save()

		# create line records
		for line_id,val in self.request.POST.iteritems():
			if 'line-item' in line_id and int(val):
				invoice_item = MyInvoiceItem.objects.get(id=int(line_id.split('-')[-1]))
				MyInvoiceReceiveItem(
					invoice_receive = invoice_receive,
					item = invoice_item,
					qty = int(val)
				).save()
		return HttpResponseRedirect(reverse_lazy('invoice_detail',kwargs={'pk':invoice.id}))

class MyInvoiceReceiveDetail(DetailView):
	model = MyInvoiceReceive
	template_name = 'erp/invoice/receive_detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		context['items'] = MyInvoiceReceiveItem.objects.filter(invoice_receive=self.object).order_by('item__inv_item__id')
		return context

@class_view_decorator(login_required)
class MyInvoiceReceiveReview(TemplateView):
	def post(self,request,pk):
		invoice_receive = MyInvoiceReceive.objects.get(id=int(pk))
		invoice_receive.reviewed_by = self.request.user
		invoice_receive.reviewed_on = dt.now()
		invoice_receive.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyInvoiceReceiveEdit(UpdateView):
	model = MyInvoiceReceive

	def post(self,request,pk):
		items = []
		for line_id,qty in self.request.POST.iteritems():
			if 'line-item-fullfill' in line_id:
				qty = int(qty)		
				f = MyInvoiceReceiveItem.objects.get(id=int(line_id.split('-')[-1]))
				if qty: 
					f.qty = qty
					f.save()
				else: f.delete()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyInvoiceReceiveDelete(DeleteView):
	model = MyInvoiceReceive
	template_name = 'erp/common/delete_form.html'

	def get_success_url(self):
		return reverse_lazy('invoice_detail',kwargs={'pk':self.object.invoice.id})

@class_view_decorator(login_required)
class MyInvoiceReceiveReviewBatch(TemplateView):
	'''
	Batch finalize all receivings linked to an invoice.
	'''
	def post(self,request,pk):
		invoice = MyInvoice.objects.get(id=int(pk))
		for rcv in MyInvoiceReceive.objects.filter(invoice=invoice):
			if not rcv.is_editable: continue
			
			rcv.reviewed_by = self.request.user
			rcv.reviewed_on = dt.now()
			rcv.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

class MyInvoiceReceiveListFilter (FilterSet):
	class Meta:
		model = MyInvoiceReceive
		fields = {
			'invoice':['exact'],
			'invoice__crm':['exact']
		}

class MyInvoiceReceiveList (FilterView):
	template_name = 'erp/invoice/receive_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MyInvoiceReceiveListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'invoice': context['filters']['invoice'] = MyInvoice.objects.get(id=int(val))
		return context

@class_view_decorator(login_required)
class MyVendorSampleInvoiceAdd(TemplateView):
	template_name = 'erp/invoice/vendor_sample_add.html'
	extra = 1
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		# invoice form
		context['form'] = VendorSampleInvoiceAddForm(initial={
			'created_by':self.request.user,
			'issued_on': dt.now(),
			'qty':self.extra
		})

		context['formset'] = formset_factory(VendorSampleInvoiceLineItemAddForm,extra=self.extra)

		# sample line item formset
		return context

	def post(self,request):
		# create invoice
		sample_invoice_form = VendorSampleInvoiceAddForm(request.POST)
		MyFormSet = formset_factory(VendorSampleInvoiceLineItemAddForm,extra=self.extra)
		formset = MyFormSet(request.POST)

		inv_items = []
		if sample_invoice_form.is_valid() and formset.is_valid():
			# TODO: this is hardcoded for now
			currency = MyCurrency.objects.get(abbrev='RMB')

			# create invoice
			invoice = sample_invoice_form.save()

			# create invoice line items
			vendor = sample_invoice_form.cleaned_data['crm']
			season = sample_invoice_form.cleaned_data['season']
			storage = sample_invoice_form.cleaned_data['storage']
			for f in formset:
				# create item
				item = MyItem(
					season = season,
					brand = vendor,
					name = f.cleaned_data['style'],
					color = f.cleaned_data['color'],
					size_chart = f.cleaned_data['size_chart'],
					currency = currency,
					price = 0
				)
				item.save()

				# Create MyItemInventory			
				for size in item.size_chart.size.split(','):
					MyItemInventory(
						item = item,
						size = size,
						storage = storage,
					).save()
				
				# create invoice line item for sample inventory item
				inv,created = MyItemInventory.objects.get_or_create(
					item = item,
					size = f.cleaned_data['sample_size'],
					storage = storage,
					item_type = 'New'
				)

				MyInvoiceItem(
					invoice = invoice,
					inv_item = inv,
					qty = 1
				).save()
			return HttpResponseRedirect(reverse_lazy('invoice_detail',kwargs={'pk':invoice.id}))
		else: 
			return render(request, self.template_name, {'form':form,'formset':formset})     

###################################################
#
#	MyPOFullfillment views
#
###################################################
class MyPOFullfillmentListFilter (FilterSet):
	class Meta:
		model = MyPOFullfillment
		fields = {
			'po':['exact'],
		}

class MyPOFullfillmentList (FilterView):
	template_name = 'erp/po/fullfill_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return MyPOFullfillmentListFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'po': context['filters']['po'] = MyPurchaseOrder.objects.get(id=int(val))
		return context

class MyPOFullfillmentDetail(DetailView):
	model = MyPOFullfillment
	template_name = 'erp/po/fullfill_detail.html'

	def get_context_data(self,**kwargs):
		context = super(DetailView,self).get_context_data(**kwargs)
		context['items'] = MyPOFullfillmentLineItem.objects.filter(po_fullfillment=self.object).order_by('po_line_item__id')
		return context

@class_view_decorator(login_required)
class MyPOFullfillmentReview(TemplateView):
	def post(self,request,pk):
		po_fullfill = MyPOFullfillment.objects.get(id=int(pk))
		po_fullfill.reviewed_by = self.request.user
		po_fullfill.reviewed_on = dt.now()
		po_fullfill.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])		

@class_view_decorator(login_required)
class MyPOFullfillmentEdit(UpdateView):
	model = MyPOFullfillment

	def post(self,request,pk):
		items = []
		for line_id,qty in self.request.POST.iteritems():
			if 'line-item-fullfill' in line_id:
				qty = int(qty)		
				f = MyPOFullfillmentLineItem.objects.get(id=int(line_id.split('-')[-1]))			
				if qty and qty != f.fullfill_qty: 
					f.fullfill_qty = qty
					f.save() # update FullfillLineItem qty
				elif qty == 0: # equal to delete this line item
					f.delete()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class MyPOFullfillmentDelete(DeleteView):
	model = MyPOFullfillment
	template_name = 'erp/common/delete_form.html'

	def get_success_url(self):
		return reverse_lazy('po_detail',kwargs={'pk':self.object.po.id})

###################################################
#
#	Menu views
#
###################################################	
class VendorNeedInvoiceList(TemplateView):
	template_name = 'erp/menu/vendor_need_invoice_list.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['vendors'] = MyCRM.objects.vendor_need_invoice()
		return context

###################################################
#
#	CRM report views
#
###################################################			
class ReportCustomerAR(TemplateView):
	template_name = 'erp/report/customer_by_ar_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		data = sorted(MyCRM.objects.customers().order_by('name'), lambda x,y: x.account_receivable>y.account_receivable)
		context['data'] = data

		# set chart height
		context['height'] = len(data)*25
		return context

class ReportVendorAP(TemplateView):
	template_name = 'erp/report/vendor_by_ap_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		data = sorted(MyCRM.objects.vendors().order_by('name'), lambda x,y: x.account_payable>y.account_payable)
		context['data'] = data

		# set chart height
		context['height'] = len(data)*25
		return context

###################################################
#
#	Product report views
#
###################################################	
class ReportTopProductBySO(TemplateView):
	template_name = 'erp/report/top_selling_items_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['data'] = data = MyItemInventory.objects.rank_by_so_qty(top=int(kwargs['top']))
		context['limited_to'] = kwargs['top']

		# compute alternative charts that can be available based on what's current
		alternatives = ['10','25','50']
		try: alternatives.remove(kwargs['top'])
		except: pass
		context['alternatives'] = alternatives

		# set chart height
		context['height'] = len(data)*25
		return context

class ReportTopProductByPO(TemplateView):
	template_name = 'erp/report/top_purchasing_items_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['data'] = data = MyItemInventory.objects.rank_by_po_qty(top=int(kwargs['top']))
		context['limited_to'] = kwargs['top']

		# compute alternative charts that can be available based on what's current
		alternatives = ['10','25','50']
		try: alternatives.remove(kwargs['top'])
		except: pass
		context['alternatives'] = alternatives

		# set chart height
		context['height'] = len(data)*25
		return context

class ReportTopProductByFullfillProfit(TemplateView):
	template_name = 'erp/report/top_fullfill_profit_items_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['data'] = data = MyItemInventory.objects.rank_by_fullfill_profit(top=int(kwargs['top']))
		context['limited_to'] = kwargs['top']

		# compute alternative charts that can be available based on what's current
		alternatives = ['10','25','50']
		try: alternatives.remove(kwargs['top'])
		except: pass
		context['alternatives'] = alternatives

		# set chart height
		context['height'] = len(data)*25
		return context

###################################################
#
#	SO report views
#
###################################################	
class ReportTopSOByQtyBalance(TemplateView):
	template_name = 'erp/report/top_so_by_qty_balance_list.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['data'] = data = MySalesOrder.objects.rank_by_qty_balance(top=int(kwargs['top']),reverse=True)
		context['limited_to'] = kwargs['top']

		# compute alternative charts that can be available based on what's current
		alternatives = ['10','25','50']
		try: alternatives.remove(kwargs['top'])
		except: pass
		context['alternatives'] = alternatives

		# set chart height
		context['height'] = len(data)*25
		return context

class ReportSOFullfillInProgress(TemplateView):
	template_name = 'erp/report/top_so_fullfill_in_progress.html'

	def get_context_data(self,**kwargs):
		context = super(TemplateView,self).get_context_data(**kwargs)
		context['data'] = data = MySalesOrder.objects.rank_by_fullfill_rate_by_qty(top=int(kwargs['top']))
		context['limited_to'] = kwargs['top']

		# compute alternative charts that can be available based on what's current
		alternatives = ['10','25','50']
		try: alternatives.remove(kwargs['top'])
		except: pass
		context['alternatives'] = alternatives

		# set chart height
		context['height'] = len(data)*25
		return context

class ReportPhysicalInventoryFilter (FilterSet):
	class Meta:
		model = MyItemInventoryPhysicalAudit
		fields = {
			'inv__item__brand':['exact'],
		}

class ReportPhysicalInventoryList (FilterView):
	template_name = 'erp/report/physical_inventory_list.html'
	paginate_by = 25

	def get_filterset_class(self):
		return ReportPhysicalInventoryFilter

	def get_context_data(self, **kwargs):
		context = super(FilterView, self).get_context_data(**kwargs)

		latest = {}
		for audit in self.object_list.order_by('-id'):
			if audit.inv not in latest: latest[audit.inv] = audit
		context['latest_list'] = latest

		# filters
		searches = context['filter']
		context['filters'] = {} # my customized filter display values
		for f,val in searches.data.iteritems():
			if val and f != "csrfmiddlewaretoken" and f != "page":
				if f == 'inv__item__brand': context['filters']['inv__item__brand'] = MyCRM.objects.get(id=int(val))
		return context

###################################################
#
#	MyLocation, MyStorage views
#
###################################################	
class MyLocationList(ListView):
	model = MyLocation
	template_name = 'erp/location/list.html'

###################################################
#
#	Myshopping cart views
#
###################################################	
@class_view_decorator(login_required)
class MyShoppingCartUpdate(TemplateView):
	def post(self,request):
		cart,created = MyShoppingCart.objects.get_or_create(user=request.user,is_open=True)

		items = []
		for line_id,qty in self.request.POST.iteritems():
			if 'inv-item' in line_id and qty:
				qty = int(qty)		
				inv_item = MyItemInventory.objects.get(id=int(line_id.split('-')[-1]))			
				shopping_cart_item,created = MyShoppingCartItem.objects.get_or_create(cart=cart,inv_item=inv_item)
				if qty: 
					shopping_cart_item.qty = qty
					shopping_cart_item.save()					
				elif qty == 0: # equal to delete this line item
					shopping_cart_item.delete()

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')	
