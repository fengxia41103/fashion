# forms.py
from django import forms
from django.forms import formset_factory
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from datetime import datetime as dt
from erp.models import *

###################################################
#
#	Contact forms
#
###################################################


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, help_text='100 characters max.')
    email = forms.EmailField(help_text='A valid email address, please.')
    subject = forms.ChoiceField(choices=(
        ('c', 'General customer service'),
        ('s', 'Suggestions'),
        ('p', 'Product support'),
    ))
    message = forms.CharField(widget=forms.Textarea)

###################################################
#
#	Attachment forms
#
###################################################


class AttachmentForm(ModelForm):

    class Meta:
        model = Attachment
        fields = ['description', 'file']

###################################################
#
#	MyItem forms
#
###################################################


class ItemImageBatchUploadForm(forms.Form):
    season = forms.ModelChoiceField(queryset=MySeason.objects.all())
    vendor = forms.ModelChoiceField(
        queryset=MyCRM.objects.vendors(), label="Brand")
    images = forms.FileField(label="Images")

###################################################
#
#	MyItemInventory forms
#
###################################################


class ItemInventoryAdjustForm(forms.Form):
    storage = forms.ModelChoiceField(queryset=MyStorage.objects.all())
    items = forms.CharField(
        widget=forms.Textarea,
        help_text=u'''Put one item per line, using syntax <span
		class="item-label">SKU #, size-qty</span>.  To enter
		size and qty, use syntax "S-1, M-2". This field is
		case insensitive.  ''' )


class ItemInventoryAddForm(ItemInventoryAdjustForm):
    # Reason
    REASON_CHOICES = (
        ('INITIAL', 'Qty is being adjusted as part of initial setup.'),
    )
    reason = forms.ChoiceField(choices=REASON_CHOICES)

###################################################
#
#	MySalesOrder forms
#
###################################################


class SalesOrderBaseForm(ModelForm):
    customer = forms.ModelChoiceField(queryset=MyCRM.objects.customers())

    class Meta:
        model = MySalesOrder
        fields = (
            'customer', 'sales', 'business_model', 'discount', 'default_storage')


class SalesOrderAddForm(SalesOrderBaseForm):
    items = forms.CharField(
        widget=forms.Textarea,
        help_text=u'''Put one item per line, using syntax <span
		class="item-label">SKU #, size-qty</span>.  To enter
		size and qty, use syntax "S-1, M-2". This field is
		case insensitive.  ''' )

    class Meta(SalesOrderBaseForm.Meta):
        fields = SalesOrderBaseForm.Meta.fields + ('items',)


class SalesOrderEditForm(ModelForm):
    customer = forms.ModelChoiceField(queryset=MyCRM.objects.customers())
    discount = forms.FloatField(max_value=1.0, min_value=0.0)

    class Meta:
        model = MySalesOrder


class SalesOrderPaymentAddForm(ModelForm):

    class Meta:
        model = MySalesOrderPayment
        fields = ['so', 'usage', 'payment_method', 'amount']
        widgets = {'so': HiddenInput()}

###################################################
#
#	MyVendorItem forms
#
###################################################


class VendorItemAddForm(ModelForm):
    price = forms.FloatField(min_value=1, initial=1.0)

    class Meta:
        model = MyVendorItem
        fields = ['product', 'vendor', 'price',
                  'currency', 'order_deadline', 'minimal_qty']
        widgets = {
            'product': HiddenInput(),
            'vendor': HiddenInput(),
            'currency': HiddenInput()
        }

###################################################
#
#	MyPurchaseOrder forms
#
###################################################


class PurchaseOrderBaseForm(ModelForm):
    vendor = forms.ModelChoiceField(queryset=MyCRM.objects.vendors())

    class Meta:
        model = MyPurchaseOrder
        fields = ('vendor', 'so', 'location')


class PurchaseOrderAddForm(PurchaseOrderBaseForm):
    items = forms.CharField(
        widget=forms.Textarea,
        help_text=u'''Put one item per line, using syntax <span
		class="item-label">SKU #, color, size-qty</span>.
		Color field would be used for partial matching so that
		you don't have to type in the entire string as they
		are shown on clothes tag.  To enter size and qty, use
		syntax "S-1, M-2". This field is case insensitive.
		''')

    class Meta(PurchaseOrderBaseForm.Meta):
        fields = PurchaseOrderBaseForm.Meta.fields + ('items',)

###################################################
#
#	MyInvoice forms
#
###################################################


class VendorInvoiceAddForm(ModelForm):
    maturity_date = forms.DateField(required=False)
    qty = forms.IntegerField(required=False)

    class Meta:
        model = MyInvoice
        fields = ('crm', 'invoice_no', 'issued_on', 'maturity_date',
                  'qty', 'gross_cost', 'discount', 'created_by')
        widgets = {'crm': HiddenInput(), 'created_by': HiddenInput()}


class VendorSampleInvoiceAddForm(ModelForm):
    season = forms.ModelChoiceField(queryset=MySeason.objects.all())
    crm = forms.ModelChoiceField(
        queryset=MyCRM.objects.vendors(), label="Brand")
    storage = forms.ModelChoiceField(queryset=MyStorage.objects.all())

    class Meta:
        model = MyInvoice
        fields = ('crm', 'season', 'storage', 'invoice_no',
                  'issued_on', 'qty', 'created_by')
        widgets = {
            'created_by': HiddenInput(),
        }


class VendorSampleInvoiceLineItemAddForm(forms.Form):
    style = forms.CharField()
    color = forms.CharField()
    size_chart = forms.ModelChoiceField(queryset=MySizeChart.objects.all())
    sample_size = forms.CharField()
    qty = forms.IntegerField(min_value=1, initial=1)
    fob = forms.FloatField(min_value=0, required=False)
