from django.contrib import admin
from erp.models import *

# Register your models here.

class MyCountryAdmin(admin.ModelAdmin):
	list_filter=['name','abbrev']
	list_display=('name','abbrev',)
admin.site.register(MyCountry,MyCountryAdmin)

class MyCurrencyAdmin(admin.ModelAdmin):
	list_filter=['name','abbrev','country']
	list_display=('name','abbrev','symbol')
admin.site.register(MyCurrency,MyCurrencyAdmin)

class MyCompanyAdmin(admin.ModelAdmin):
	list_filter=['name','abbrev']
admin.site.register(MyCompany,MyCompanyAdmin)

class MyExchangeRateAdmin(admin.ModelAdmin):
	list_filter=['home','foreign','rate']
admin.site.register(MyExchangeRate,MyExchangeRateAdmin)

class MyItemAdmin(admin.ModelAdmin):
	list_filter=['season','brand']
	list_display = ['season','brand','name','color','price','size_chart']
admin.site.register(MyItem,MyItemAdmin)

class MyVendorItemAdmin(admin.ModelAdmin):
	list_filter=['vendor','currency','order_deadline']
	list_display=('vendor','product','price','order_deadline','minimal_qty')
admin.site.register(MyVendorItem,MyVendorItemAdmin)

class MyReturnReasonAdmin(admin.ModelAdmin):
	list_display = ('category','name','description','result_type','code')
admin.site.register(MyReturnReason,MyReturnReasonAdmin)

admin.site.register(MyUOM)
admin.site.register(MyFiscalYear)
admin.site.register(MyStorage)
admin.site.register(MyLocation)
admin.site.register(MyCRM)
admin.site.register(MySeason)
admin.site.register(MyItemInventory)
admin.site.register(MySalesOrder)
admin.site.register(MySalesOrderLineItem)
admin.site.register(MyPurchaseOrder)
admin.site.register(MyPurchaseOrderLineItem)
admin.site.register(MySalesOrderFulfillment)
admin.site.register(MySalesOrderFulfillmentLineItem)
admin.site.register(MySizeChart)
admin.site.register(MyBusinessModel)