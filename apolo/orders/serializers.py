import requests
from apolo.orders.models import Orders, ProductOrders
from apolo.products.models import Products, Stock, StockTracer
from rest_framework import serializers
from django.db import transaction


class ProductOrdersReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrders
        fields = "__all__"


class OrderReaderSerializer(serializers.ModelSerializer):
    productorders_set = ProductOrdersReaderSerializer(many=True)

    class Meta:
        model = Orders
        fields = ["id", "productorders_set"]


class OrderSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.DictField(
        )
    )

    @classmethod
    def get_product(cls, id):
        response = requests.get(f"http://127.0.0.1:8000/api/v1/products/?id={id}")
        if response.ok:
            product = response.json()["results"]
            if not product:
                return False, {"error": f"Product does not exist with id: {id}"}
            return True, product[0]
        return False, {"error": "Something wrong has happend"}
    
    @classmethod
    def verify_stock(cls, id, quantity):
        response = requests.get(f"http://127.0.0.1:8000/api/v1/products/{id}/validate_stock/?quantity={quantity}&flow=OUT")
        if response.ok:
            product = response.json()
            if not product:
                return False, {"error": f"Product does not exist with id: {id}"}
            return True, product
        try:
            for key in response.json().keys():
                message = response.json().get(key, "Something wrong had happend")
        except:
            message = "Something wrong had happend"
        return False, {"error": message}
    
    def _discount_stock(self, product):
        quantity = product["quantity"]
        product_id = product["id"]
        flow = "OUT"
        payload = {'quantity': quantity, 'flow': flow}

        response = requests.put(f"http://127.0.0.1:8000/api/v1/products/{product_id}/update_stock/", data=payload)
        tracer_id = response.json()["tracer_id"]
        return tracer_id

    def create(self, validated_data, *args, **kwargs):
        for product in kwargs["context"]["products"]:
            order = Orders.objects.create()
            tracer_id = self._discount_stock(product)
            ProductOrders.objects.create(
                stock_tracer_id=tracer_id,
                product_id=product["id"],
                product_name=product["name"],
                quantity=product["quantity"],
                price_per_unit=product["stock"][0]["price_per_unit"],
                order=order,
            )
        return order