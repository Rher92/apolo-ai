from django.db.models import OuterRef, Subquery

from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from apolo.orders.models import Orders
from apolo.orders.serializers import OrderReaderSerializer, OrderSerializer

class OrdersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Orders.objects.all()

    def get_serializer_class(self):
        if self.action in ["create"]:
            return OrderSerializer
        return OrderReaderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        errors = []
        products = []
        for product in serializer.data.get("products", []):
            is_ok_product, response_product = OrderSerializer.get_product(product["id"])
            if not is_ok_product:
                errors.append(response_product)
            else:
                response_product["quantity"] = product["quantity"]
                products.append(response_product)
            is_ok_stock, response_stock = OrderSerializer.verify_stock(product["id"], product["quantity"])
            if not is_ok_stock:
                errors.append(response_stock)

        if errors:
            return Response({"message": errors}, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.create(validated_data=serializer.validated_data, context={"products": products})
        data = OrderReaderSerializer(product).data
        return Response(data, status=status.HTTP_201_CREATED)