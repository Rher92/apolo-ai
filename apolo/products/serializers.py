from apolo.orders.models import Orders
from apolo.products.models import Products, Stock, StockTracer
from rest_framework import serializers



class StockReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['quantity', 'price_per_unit']


class ProductReaderSerializer(serializers.ModelSerializer):
    stock = StockReaderSerializer(many=True)

    class Meta:
        model = Products
        fields = ['id', 'name', 'stock']


class ProductStockValidatorSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True)
    flow = serializers.ChoiceField(
        choices=StockTracer.Flows.choices,
        required=True
    )
    
    def validate_flow(self, value):
        if not value in StockTracer.Flows:
            raise serializers.ValidationError("Flow does not exist")
        return value            

    def validate(self, data):
        if data["flow"] == StockTracer.Flows.OUT:
            instance = self.context["instance"]
            if instance.quantity == 0:
                raise serializers.ValidationError("Product does not have stock")
            if data["quantity"] > instance.quantity:
                raise serializers.ValidationError("Product does not have stock enough to this order")
        else:
            if data["quantity"] < 1:
                raise serializers.ValidationError("Quantity must have greater than 0")
        return data

    def update(self, instance, validated_data):
        stock = instance.stock.first()
        tracer = StockTracer.objects.create(
            product=instance,
            stock=stock,
            product_name=instance.name,
            quantity=validated_data["quantity"],
            price_per_unit=stock.price_per_unit,
            flow=validated_data["flow"]
        )
        self.context["tracer_id"] = tracer.id
        return instance


class ProductEditorSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    price_per_unit = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    def validate_name(self, value):
        instance = self.context["instance"]
        if Products.objects.filter(name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Product already exists")
        return value

    def validate_price_per_unit(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.save(update_fields=["name"])   
        stock = instance.stock.first()
        stock.price_per_unit = validated_data["price_per_unit"]
        stock.save(update_fields=["price_per_unit"])
        return instance


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    price_per_unit = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(required=False)

    def validate_name(self, value):
        if Products.objects.filter(name=value).exists():
            raise serializers.ValidationError("Product already exists")
        return value

    def validate_price_per_unit(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity(self, value):
        if value:
            if value < 0:
                raise serializers.ValidationError("Price must be greater than 0")
            return value

    def create(self, validated_data):
        product =  Products.objects.create(name=validated_data["name"])
        stock = Stock.objects.create(
            product=product,
            quantity=validated_data["quantity"],
            price_per_unit=validated_data["price_per_unit"]
        )
        StockTracer.objects.create(
            product=product,
            stock=stock,
            product_name=validated_data["name"],
            price_per_unit=validated_data["price_per_unit"],
            flow=StockTracer.Flows.IN
        )

        return product
        