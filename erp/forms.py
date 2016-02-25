# forms.py
from django import forms
from django.forms import formset_factory
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from erp.models import *

class AttachmentForm(ModelForm):
	class Meta:
		model = Attachment
		fields = ['description','file']

class ItemInventoryAdjustForm(forms.Form):
	storage = forms.ModelChoiceField(queryset=MyStorage.objects.all())
	items = forms.CharField(
		widget=forms.Textarea,
		help_text = u'''Put one item per line, using syntax <span class="item-label">SKU #, color, size-qty</span>. 
		Color field would be
		used for partial matching so that you don't have to type in the entire string as they are shown on clothes tag. 
		To enter size and qty, use syntax "S-1, M-2". This field is case insensitive.
		'''
	)

class ItemInventoryAddForm(ItemInventoryAdjustForm):
	# Reason
	REASON_CHOICES = (
		('INITIAL','Qty is being adjusted as part of initial setup.'),
	)
	reason = forms.ChoiceField(choices = REASON_CHOICES)

class SalesOrderBaseForm(ModelForm):
	customer = forms.ModelChoiceField(queryset=MyCRM.objects.filter(Q(crm_type='C')|Q(crm_type='B')))
	class Meta:
		model = MySalesOrder
		fields = ('customer','sales','business_model','discount','default_storage')

class SalesOrderAddForm(SalesOrderBaseForm):
	items = forms.CharField(
		widget=forms.Textarea,
		help_text = u'''Put one item per line, using syntax <span class="item-label">SKU #, color, size-qty</span>. 
		Color field would be
		used for partial matching so that you don't have to type in the entire string as they are shown on clothes tag. 
		To enter size and qty, use syntax "S-1, M-2". This field is case insensitive.
		'''
	)

	class Meta(SalesOrderBaseForm.Meta):
		fields = SalesOrderBaseForm.Meta.fields + ('items',)

class SalesOrderEditForm(ModelForm):
	customer = forms.ModelChoiceField(queryset=MyCRM.objects.filter(Q(crm_type='C')|Q(crm_type='B')))
	discount = forms.FloatField(max_value=1.0,min_value=0.0)
	class Meta:
		model = MySalesOrder

class VendorItemForm(ModelForm):
	class Meta:
		model = MyVendorItem

class SalesOrderPaymentAddForm(ModelForm):
	class Meta:
		model = MySalesOrderPayment
		fields = ['so','usage','payment_method','amount']		
		widgets = {'so': HiddenInput()}
