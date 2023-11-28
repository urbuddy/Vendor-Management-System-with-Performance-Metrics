from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Vendor, PurchaseOrder, PerformanceHistory
from datetime import datetime, timedelta


class VendorManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test vendor
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="test@example.com",
            address="123 Test St",
            vendor_code="V001"
        )

        # Create test purchase order
        self.purchase_order = PurchaseOrder.objects.create(
            vendor=self.vendor,
            po_number="PO001",
            order_date=datetime.now(),
            delivery_date=datetime.now() + timedelta(days=7),
            items={"item": "Test item"},
            quantity=10,
            status="pending",
            quality_rating=4.5,
            acknowledgment_date=datetime.now() - timedelta(days=1)
        )

        # Create historical performance for the vendor
        PerformanceHistory.objects.create(
            vendor=self.vendor,
            on_time_delivery_rate=95.0,
            quality_rating_avg=4.8,
            average_response_time=24.0,
            fulfillment_rate=98.0
        )

    def test_vendor_endpoints(self):
        # Test creating a new vendor
        new_vendor_data = {
            "name": "New Vendor",
            "contact_details": "new_vendor@example.com",
            "address": "456 New St",
            "vendor_code": "V002"
        }
        response = self.client.post(reverse('vendors'), new_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test retrieving the list of vendors
        response = self.client.get(reverse('vendors'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming there are two vendors now

        # Test retrieving details of a specific vendor
        response = self.client.get(reverse('vendor', args=[self.vendor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Vendor")

        # Test updating a vendor's details
        updated_vendor_data = {"name": "Updated Vendor"}
        response = self.client.put(reverse('vendor', args=[self.vendor.id]), updated_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Vendor")

        # Test deleting a vendor
        response = self.client.delete(reverse('vendor', args=[self.vendor.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vendor.objects.count(), 1)

    def test_purchase_order_endpoints(self):
        # Test creating a new purchase order
        new_purchase_order_data = {
            "vendor": self.vendor.id,
            "po_number": "PO002",
            "order_date": datetime.now().isoformat(),
            "delivery_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "items": {"item": "New Test item"},
            "quantity": 5,
            "status": "pending",
            "quality_rating": 4.0,
            "acknowledgment_date": (datetime.now() - timedelta(days=2)).isoformat()
        }
        response = self.client.post(reverse('orders'), new_purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test retrieving the list of purchase orders
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming there are two purchase orders now

        # Test retrieving details of a specific purchase order
        response = self.client.get(reverse('order', args=[self.purchase_order.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['po_number'], "PO001")

        # Test updating a purchase order
        updated_purchase_order_data = {"status": "completed"}
        response = self.client.put(reverse('order', args=[self.purchase_order.id]), updated_purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "completed")

        # Test deleting a purchase order
        response = self.client.delete(reverse('order', args=[self.purchase_order.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseOrder.objects.count(), 1)

    def test_vendor_performance_endpoint(self):
        response = self.client.get(reverse('performance', args=[self.vendor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('on_time_delivery_rate', response.data)
        self.assertIn('quality_rating_avg', response.data)
        self.assertIn('average_response_time', response.data)
        self.assertIn('fulfillment_rate', response.data)

    def test_update_acknowledgment_endpoint(self):
        purchase_order_id = self.purchase_order.id
        acknowledgment_data = {"acknowledgment_date": datetime.now().isoformat()}
        response = self.client.post(reverse('acknowledge_order', args=[purchase_order_id]), acknowledgment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assuming acknowledgment_date is updated and average_response_time should be recalculated
        updated_purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        self.assertIsNotNone(updated_purchase_order.acknowledgment_date)
        self.assertNotEqual(updated_purchase_order.average_response_time, 0.0)

    def test_historical_performance_model(self):
        historical_performance = PerformanceHistory.objects.first()
        self.assertIsNotNone(historical_performance)
        self.assertEqual(historical_performance.vendor, self.vendor)
        self.assertEqual(historical_performance.on_time_delivery_rate, 95.0)
        self.assertEqual(historical_performance.quality_rating_avg, 4.8)
        self.assertEqual(historical_performance.average_response_time, 24.0)
        self.assertEqual(historical_performance.fulfillment_rate, 98.0)
