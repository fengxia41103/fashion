from django.conf.urls import patterns, url
from django.conf.urls import url
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.views as AuthViews
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from erp import views

urlpatterns = patterns(
		'',
		# url(r'^$', views.HomeView.as_view(), name='home'),
		url(r'^$', views.LoginView.as_view(), name='home'),
		url(r'login/$', views.LoginView.as_view(),name='login'),
		url(r'logout/$', views.LogoutView.as_view(), name='logout'),
		url(r'^register/$', views.UserRegisterView.as_view(), name='user_register'),

		# attachments
		url(r'^attachment/(?P<pk>\d+)/delete/$', views.attachment_delete_view, name='attachment_delete'),
		url(r'^attachment/item/(?P<pk>\d+)/add/$', views.item_attachment_add_view, name='item_attachment_add'),
		url(r'^attachment/crm/(?P<pk>\d+)/add/$', views.crm_attachment_add_view, name='crm_attachment_add'),
		
		# fiscalyears
		url(r'^fiscalyears/$', views.MyFiscalYearList.as_view(), name='fiscalyear_list'),
		url(r'^fiscalyear/add/$', views.MyFiscalYearAdd.as_view(), name='fiscalyear_add'),
		url(r'^fiscalyear/(?P<pk>\d+)/delete/$', views.MyFiscalYearDelete.as_view(), name='fiscalyear_delete'),

		# items
		url(r'^items/$', views.MyItemList.as_view(), name='item_list'),		
		url(r'^item/add/$', views.MyItemAdd.as_view(), name='item_add'),
		url(r'^item/(?P<pk>\d+)/$', views.MyItemDetail.as_view(), name='item_detail'),		
		url(r'^item/(?P<pk>\d+)/edit/$', views.MyItemEdit.as_view(), name='item_edit'),
		url(r'^item/(?P<pk>\d+)/delete/$', views.MyItemDelete.as_view(), name='item_delete'),
		url(r'^item/inv/add/$', views.MyItemInventoryAdd.as_view(), name='item_inv_add'),	
		url(r'^items/(?P<season>\d+)/(?P<brand>\d+)/$', views.MyItemListByVendor.as_view(), name='item_list_by_vendor'),		

		# season
		url(r'^seasons/$', views.MySeasonList.as_view(), name='season_list'),		
		url(r'^season/(?P<pk>\d+)/$', views.MySeasonDetail.as_view(), name='season_detail'),		

		# crms
		url(r'^vendors/$', views.MyVendorList.as_view(), name='vendor_list'),		
		url(r'^vendor/add/$', views.MyVendorAdd.as_view(), name='vendor_add'),
		url(r'^vendor/(?P<pk>\d+)/edit/$', views.MyVendorEdit.as_view(), name='vendor_edit'),
		url(r'^vendor/(?P<pk>\d+)/$', views.MyVendorDetail.as_view(), name='vendor_detail'),

		url(r'^customers/$', views.MyCustomerList.as_view(), name='customer_list'),	
		url(r'^customer/add/$', views.MyCustomerAdd.as_view(), name='customer_add'),		
		url(r'^customer/(?P<pk>\d+)/edit/$', views.MyCustomerEdit.as_view(), name='customer_edit'),

		# Business model
		url(r'^bizmodel/add/$', views.MyBusinessModelAdd.as_view(), name='biz_model_add'),		

		# Sales Order
		url(r'^so/$', views.MySalesOrderList.as_view(), name='so_list'),	
		url(r'^so/add/$', views.MySalesOrderAdd.as_view(), name='so_add'),		
		url(r'^so/(?P<pk>\d+)/$', views.MySalesOrderDetail.as_view(), name='so_detail'),
		url(r'^so/add/item/$', views.MySalesOrderAddItem.as_view(), name='so_add_item'),
		url(r'^so/remove/item/(?P<pk>\d+)/$', views.MySalesOrderLineItemDelete.as_view(), name='so_remove_item'),
		url(r'^so/edit/(?P<pk>\d+)/$', views.MySalesOrderEdit.as_view(), name='so_edit'),
		url(r'^so/delete/(?P<pk>\d+)/$', views.MySalesOrderDelete.as_view(), name='so_delete'),

		# Sales order fullfillment
		url(r'^so/fullfill/add/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentAdd.as_view(), name='so_fullfill_add'),		
		url(r'^so/fullfill/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentDetail.as_view(), name='so_fullfill_detail'),
		url(r'^so/fullfill/edit/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentEdit.as_view(), name='so_fullfill_edit'),		
		url(r'^so/fullfill/delete/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentDelete.as_view(), name='so_fullfill_delete'),		

		# Sales order return
		url(r'^so/return/add/(?P<pk>\d+)/$', views.MySalesOrderReturnAdd.as_view(), name='so_return_add'),		
		url(r'^so/return/(?P<pk>\d+)/$', views.MySalesOrderReturnDetail.as_view(), name='so_return_detail'),
		url(r'^so/return/edit/(?P<pk>\d+)/$', views.MySalesOrderReturnEdit.as_view(), name='so_return_edit'),		
		url(r'^so/return/delete/(?P<pk>\d+)/$', views.MySalesOrderReturnDelete.as_view(), name='so_return_delete'),		

		# Sales order payment
		url(r'^so/payments/$', views.MySalesOrderPaymentList.as_view(), name='so_payment_list'),						
		url(r'^so/payment/add/$', views.MySalesOrderPaymentAdd.as_view(), name='so_payment_add'),
	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
