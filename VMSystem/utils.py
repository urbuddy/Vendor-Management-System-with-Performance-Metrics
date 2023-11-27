from django.db.models import F, Avg
from .models import *


def calculate_on_time_delivery_rate(vendor):
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_pos.filter(delivery_date__lte=F('acknowledgment_date'))
    on_time_delivery_rate = on_time_deliveries.count() / completed_pos.count() * 100 if completed_pos.count() > 0 else 0
    return on_time_delivery_rate


def calculate_quality_rating_avg(vendor):
    completed_pos_with_ratings = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)
    quality_rating_avg = completed_pos_with_ratings.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0
    return quality_rating_avg


def calculate_average_response_time(vendor):
    completed_pos_with_acknowledgment = PurchaseOrder.objects.filter(vendor=vendor, status='completed', acknowledgment_date__isnull=False)
    response_times = ((po.acknowledgment_date - po.issue_date).total_seconds() for po in completed_pos_with_acknowledgment)
    average_response_time = (sum(response_times) / len(response_times) if len(response_times) > 0 else 0)
    return average_response_time


# def calculate_vendor_average_response_time(vendor):
#     completed_pos_with_acknowledgment = PurchaseOrder.objects.filter(vendor=vendor, status='completed', acknowledgment_date__isnull=False)
#     total_completed_pos = completed_pos_with_acknowledgment.count()
#
#     if total_completed_pos == 0:
#         return 0  # No completed orders with acknowledgment, average response time is 0
#
#     response_times = [po.response_time for po in completed_pos_with_acknowledgment if po.response_time is not None]
#     average_response_time = sum(response_times) / total_completed_pos
#     return average_response_time


def calculate_fulfillment_rate(vendor):
    total_pos = PurchaseOrder.objects.filter(vendor=vendor)
    successful_fulfillments = total_pos.filter(status='completed', issues__isnull=True)
    fulfillment_rate = successful_fulfillments.count() / total_pos.count() * 100 if total_pos.count() > 0 else 0
    return fulfillment_rate
