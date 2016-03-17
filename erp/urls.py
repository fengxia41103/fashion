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
		url(r'^items/(?P<season>\d+)/(?P<brand>\d+)/$', views.MyItemListByVendor.as_view(), name='item_list_by_vendor'),		

		# inventory
		url(r'^item/inv/add/$', views.MyItemInventoryAdd.as_view(), name='item_inv_add'),	
		url(r'^item/inv/physical/(?P<storage>\d+)/(?P<vendor>\d+)/$', views.MyItemInventoryPhysicalAdd.as_view(), name='item_inv_physical_add'),	

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
		url(r'^so/2po/(?P<pk>\d+)/$', views.MySalesOrderToPurchaseOrder.as_view(), name='so_to_po'),
		url(r'^so/qty/$', views.MySalesOrderLineItemUpdateQty.as_view(), name='so_update_qty'),

		# Sales order fullfillment
		url(r'^so/fullfills/$', views.MySalesOrderFullfillmentList.as_view(), name='so_fullfill_list'),		
		url(r'^so/fullfill/add/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentAdd.as_view(), name='so_fullfill_add'),		
		url(r'^so/fullfill/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentDetail.as_view(), name='so_fullfill_detail'),
		url(r'^so/fullfill/edit/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentEdit.as_view(), name='so_fullfill_edit'),		
		url(r'^so/fullfill/delete/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentDelete.as_view(), name='so_fullfill_delete'),		
		url(r'^so/fullfill/review/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentReview.as_view(), name='so_fullfill_review'),		
		url(r'^so/fullfill/review/batch/(?P<pk>\d+)/$', views.MySalesOrderFullfillmentReviewBatch.as_view(), name='so_fullfill_review_batch'),		

		# Sales order return
		url(r'^so/returns/$', views.MySalesOrderReturnList.as_view(), name='so_return_list'),		
		url(r'^so/return/add/(?P<pk>\d+)/$', views.MySalesOrderReturnAdd.as_view(), name='so_return_add'),		
		url(r'^so/return/(?P<pk>\d+)/$', views.MySalesOrderReturnDetail.as_view(), name='so_return_detail'),
		url(r'^so/return/edit/(?P<pk>\d+)/$', views.MySalesOrderReturnEdit.as_view(), name='so_return_edit'),		
		url(r'^so/return/delete/(?P<pk>\d+)/$', views.MySalesOrderReturnDelete.as_view(), name='so_return_delete'),		
		url(r'^so/return/review/(?P<pk>\d+)/$', views.MySalesOrderReturnReview.as_view(), name='so_return_review'),		
		url(r'^so/return/review/batch/(?P<pk>\d+)/$', views.MySalesOrderReturnReviewBatch.as_view(), name='so_return_review_batch'),		
		url(r'^so/return/review/undo/(?P<pk>\d+)/$', views.MySalesOrderReturnReviewUndo.as_view(), name='so_return_review_undo'),		

		# Sales order payment
		url(r'^so/payments/$', views.MySalesOrderPaymentList.as_view(), name='so_payment_list'),						
		url(r'^so/payment/add/$', views.MySalesOrderPaymentAdd.as_view(), name='so_payment_add'),
		url(r'^so/payment/review/(?P<pk>\d+)/$', views.MySalesOrderPaymentReview.as_view(), name='so_payment_review'),		
		url(r'^so/payment/delete/(?P<pk>\d+)/$', views.MySalesOrderPaymentDelete.as_view(), name='so_payment_delete'),		

		# VendorItem
		url(r'^vendor/items/$', views.MyVendorItemList.as_view(), name='vendor_item_list'),	
		url(r'^vendor/item/add/$', views.MyVendorItemAdd.as_view(), name='vendor_item_add'),
		url(r'^vendor/item/edit/(?P<pk>\d+)/$', views.MyVendorItemEdit.as_view(), name='vendor_item_edit'),
		url(r'^vendor/item/delete/(?P<pk>\d+)/$', views.MyVendorItemDelete.as_view(), name='vendor_item_delete'),

		# Purchase order
		url(r'^po/$', views.MyPurchaseOrderList.as_view(), name='po_list'),	
		url(r'^po/add/$', views.MyPurchaseOrderAdd.as_view(), name='po_add'),		
		url(r'^po/(?P<pk>\d+)/$', views.MyPurchaseOrderDetail.as_view(), name='po_detail'),
		url(r'^po/delete/(?P<pk>\d+)/$', views.MyPurchaseOrderDelete.as_view(), name='po_delete'),
		url(r'^po/place/(?P<pk>\d+)/$', views.MyPurchaseOrderPlace.as_view(), name='po_place'),
		url(r'^po/avaibility/$', views.MyPurchaseOrderLineItemUpdateAvailability.as_view(), name='po_availability'),

		# Purchase order fullfillment
		url(r'^po/fullfills/$', views.MyPOFullfillmentList.as_view(), name='po_fullfill_list'),		
		url(r'^po/fullfill/(?P<pk>\d+)/$', views.MyPOFullfillmentDetail.as_view(), name='po_fullfill_detail'),		
		url(r'^po/fullfill/review/(?P<pk>\d+)/$', views.MyPOFullfillmentReview.as_view(), name='po_fullfill_review'),		
		url(r'^po/fullfill/edit/(?P<pk>\d+)/$', views.MyPOFullfillmentEdit.as_view(), name='po_fullfill_edit'),		
		url(r'^po/fullfill/delete/(?P<pk>\d+)/$', views.MyPOFullfillmentDelete.as_view(), name='po_fullfill_delete'),		

		# Invoice
		url(r'^invoices/$', views.MyInvoiceList.as_view(), name='invoice_list'),	
		url(r'^invoice/vendor/add/(?P<pk>\d+)/$', views.MyVendorInvoiceAdd.as_view(), name='vendor_invoice_add'),	
		url(r'^invoice/(?P<pk>\d+)/$', views.MyInvoiceDetail.as_view(), name='invoice_detail'),
		url(r'^invoice/delete/(?P<pk>\d+)/$', views.MyInvoiceDelete.as_view(), name='invoice_delete'),
		url(r'^invoice/edit/(?P<pk>\d+)/$', views.MyInvoiceEdit.as_view(), name='invoice_edit'),
		url(r'^invoice/review/(?P<pk>\d+)/$', views.MyInvoiceReview.as_view(), name='invoice_review'),		
		url(r'^invoice/line/edit/(?P<pk>\d+)/$', views.MyInvoiceLineItemEdit.as_view(), name='invoice_line_edit'),

		# Invoice receive
		url(r'^invoice/receives/$', views.MyInvoiceReceiveList.as_view(), name='invoice_receive_list'),		
		url(r'^invoice/receive/add/(?P<pk>\d+)/$', views.MyInvoiceReceiveAdd.as_view(), name='invoice_receive_add'),		
		url(r'^invoice/receive/(?P<pk>\d+)/$', views.MyInvoiceReceiveDetail.as_view(), name='invoice_receive_detail'),
		url(r'^invoice/receive/review/(?P<pk>\d+)/$', views.MyInvoiceReceiveReview.as_view(), name='invoice_receive_review'),		
		url(r'^invoice/receive/edit/(?P<pk>\d+)/$', views.MyInvoiceReceiveEdit.as_view(), name='invoice_receive_edit'),		
		url(r'^invoice/receive/delete/(?P<pk>\d+)/$', views.MyInvoiceReceiveDelete.as_view(), name='invoice_receive_delete'),		
		url(r'^invoice/receive/review/batch/(?P<pk>\d+)/$', views.MyInvoiceReceiveReviewBatch.as_view(), name='invoice_receive_review_batch'),		

		# Menu
		url(r'^menu/vendor/need/invoice/$', views.VendorNeedInvoiceList.as_view(), name='vendor_need_invoice_list'),		

		# Location and storage
		url(r'^locations/$', views.MyLocationList.as_view(), name='location_list'),		

		# Report
		url(r'^report/customer/ar/$', views.ReportCustomerAR.as_view(), name='customer_ar_report'),		
		url(r'^report/vendor/ap/$', views.ReportVendorAP.as_view(), name='vendor_ap_report'),		
		url(r'^report/top/selling/product/(?P<top>\d+)/$', views.ReportTopProductBySO.as_view(), name='top_selling_product_report'),		
		url(r'^report/top/purchasing/product/(?P<top>\d+)/$', views.ReportTopProductByPO.as_view(), name='top_purchasing_product_report'),		
		url(r'^report/top/fullfill/profit/product/(?P<top>\d+)/$', views.ReportTopProductByFullfillProfit.as_view(), name='top_fullfill_profit_product_report'),		
		url(r'^report/top/so/qty/balance/(?P<top>\d+)/$', views.ReportTopSOByQtyBalance.as_view(), name='top_so_qty_balance_report'),		
		url(r'^report/top/so/fullfill/rate/qty/(?P<top>\d+)/$', views.ReportSOFullfillInProgress.as_view(), name='top_so_fullfill_in_progress_report'),		
		url(r'^report/physical/inventory/$', views.ReportPhysicalInventoryList.as_view(), name='latest_physical_inventory_report'),		

	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
