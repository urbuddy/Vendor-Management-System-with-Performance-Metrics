from .utils import *
from .Serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


# Create your views here.


class VendorsDetails(APIView):
    def get(self, request):
        obj = Vendor.objects.all()
        serializer = VendorSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class VendorInfo(APIView):
    def get(self, request, id):
        try:
            obj = Vendor.objects.get(id=id)
        except(KeyError, Vendor.DoesNotExist):
            msg = {'msg': 'vendor not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            obj = Vendor.objects.get(id=id)
            serializer = VendorSerializer(obj, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        except Vendor.DoesNotExist:
            msg = {"msg": "vendor not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            obj = Vendor.objects.get(id=id)
        except Vendor.DoesNotExist:
            msg = {'msg': 'vendor not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        performance_history = PerformanceHistory.objects.get(vendor=obj)
        if performance_history.count() > 0:
            performance_history.delete()
        obj.delete()
        return Response({'msg': 'vendor deleted'}, status=status.HTTP_204_NO_CONTENT)


class POsDetails(APIView):
    def get(self, request):
        obj = PurchaseOrder.objects.all()
        serializer = POSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = POSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['quality_rating'] != None:
                try:
                    vendor = Vendor.objects.get_or_create(id=serializer.validated_data['vendor'])
                    performance = PerformanceHistory.objects.get(vendor=vendor)
                    performance.quality_rating_avg = calculate_quality_rating_avg(vendor)
                    vendor.quality_rating_avg = performance.quality_rating_avg
                    performance.save()
                    vendor.save()
                except ZeroDivisionError as error:
                    print(error)
                    msg = {'msg': 'divide by zero error occurred'}
                    return Response(msg, status=status.HTTP_400_BAD_REQUEST)
                except Exception as error:
                    print(error)
                    msg = {'msg': error}
                    return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class POInfo(APIView):
    def get(self, request, id):
        try:
            obj = PurchaseOrder.objects.get(id=id)
        except PurchaseOrder.DoesNotExist:
            msg = {'msg': 'order not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        serializer = POSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            obj = PurchaseOrder.objects.get(id=id)
            serializer = POSerializer(obj, data=request.data)
            if serializer.is_valid():
                if serializer.validated_data['status'] == 'completed':
                    vendor = Vendor.objects.get(id=obj.vendor__id)
                    vendor.on_time_delivery_rate = calculate_on_time_delivery_rate(vendor)
                    vendor.fulfillment_rate = calculate_fulfillment_rate(vendor)
                    if obj.quality_rating != None:
                        vendor.quality_rating_avg = calculate_quality_rating_avg(vendor)
                    vendor.save()
                    performance = PerformanceHistory.objects.get_or_create(vendor=vendor, on_time_delivery_rate=vendor.on_time_delivery_rate, quality_rating_avg=vendor.quality_rating_avg, fulfillment_rate=vendor.fulfillment_rate)
                    performance.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseOrder.DoesNotExist:
            msg = {'msg': 'order not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        except ZeroDivisionError as error:
            print(error)
            msg = {'msg': 'divide by zero error occurred'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            msg = {'msg': error}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            obj = PurchaseOrder.objects.get(id=id)
        except PurchaseOrder.DoesNotExist:
            msg = {'msg': 'order not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'msg': 'order deleted'}, status=status.HTTP_204_NO_CONTENT)


class PerformanceInfo(APIView):
    def get(self, request, id):
        try:
            obj = PerformanceHistory.objects.get(id=id)
        except PerformanceHistory.DoesNotExist:
            msg = {'msg': 'peformance record not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        serializer = PHSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcknowledgeOrder(APIView):
    def patch(self, request, id):
        try:
            obj = PurchaseOrder.objects.get(id=id)
            serializer = POSerializer(obj, data=request.data, partial=True)
            if serializer.is_valid():
                vendor = Vendor.objects.get(id=obj.vendor__id)
                performance = PerformanceHistory.objects.get(vendor=vendor)
                performance.quality_rating_avg = calculate_quality_rating_avg(vendor)
                performance.average_response_time = calculate_average_response_time(vendor)
                vendor.quality_rating_avg = performance.quality_rating_avg
                vendor.average_response_time = performance.average_response_time()
                performance.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseOrder.DoesNotExist:
            msg = {'msg': 'order not found'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        except ZeroDivisionError as error:
            print(error)
            msg = {'msg': 'divide by zero error occurred'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            msg = {'msg': error}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)