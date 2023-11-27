from django.contrib import admin
from .models import *


# Register your models here.


class VendorAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'vendor_code', 'contact_details', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time',
    'fulfillment_rate')


class POAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'order_date', 'delivery_date', 'status', 'quantity', 'quality_rating')


class PHAdmin(admin.ModelAdmin):
    list_display = (
    'vendor', 'date', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate')


admin.site.register(Vendor, VendorAdmin)
admin.site.register(PurchaseOrder, POAdmin)
admin.site.register(PerformanceHistory, PHAdmin)
