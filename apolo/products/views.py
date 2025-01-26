from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from apolo.products.models import Products, Stock
from apolo.products.serializers import ProductEditorSerializer, ProductReaderSerializer, ProductSerializer, ProductStockValidatorSerializer


class ProductFilter(filters.FilterSet):
    id = filters.CharFilter(method='filter_by_ids')

    class Meta:
        model = Products
        fields = ['id']

    def filter_by_ids(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(id__in=ids)


class ProductsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Products.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id"]

    def get_queryset(self):
        _stock = Stock.objects.filter(
            product=OuterRef("pk")
        )
        product =  (
            Products.objects.all()
            .annotate(
                price_per_unit=Subquery(
                   _stock.values("price_per_unit")[:1]
                )
            )
            .annotate(
                quantity=Subquery(
                   _stock.values("quantity")[:1]
                )
            )
        )
        return product

    def get_serializer_class(self):
        if self.action in ["create"]:
            return ProductSerializer
        elif self.action in ["update", "partial_update"]:
            return ProductEditorSerializer
        elif self.action in ["validate_stock", "update_stock"]:
            return ProductStockValidatorSerializer
        return ProductReaderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        product.refresh_from_db()
        data = ProductReaderSerializer(product).data
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"instance": instance},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        data = ProductReaderSerializer(instance).data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def validate_stock(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.GET,
            context={"instance": instance},
        )
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Enough stock"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def update_stock(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            context={"instance": instance, "tracer_id": None},
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "OK", "tracer_id": serializer.context["tracer_id"]}, status=status.HTTP_200_OK)