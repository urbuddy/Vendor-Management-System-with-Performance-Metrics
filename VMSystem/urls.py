from django.urls import path
from .views import *


urlpatterns = [
    path('vendors/', VendorsDetails.as_view(), name='vendors'),
    path('vendors/<int:id>', VendorInfo.as_view(), name='vendor'),

    path('purchase_orders/', POsDetails.as_view(), name='orders'),
    path('purchase_orders/<int:id>', POsDetails.as_view(), name='order'),
    path('purchase_orders/<int:id>/acknowledge', AcknowledgeOrder.as_view(), name='acknowledge_order'),

    path('vendors/<int:id>/performance', PerformanceInfo.as_view(), name='performance'),
]