from django.db import models

from apolo.products.models import Products, StockTracer
from apolo.utils.models import MetaModel


class Orders(MetaModel):
    def __str__(self):
        return f"Order ID: {self.pk}"


class ProductOrders(MetaModel):
    stock_tracer_id = models.CharField(
        blank=False,
        null=False,
        max_length=100
    )
    product_id = models.CharField(
        blank=False,
        null=False,
        max_length=100
    )
    product_name = models.CharField(
        blank=False,
        null=False,
        max_length=100
    )
    quantity = models.IntegerField(
        null=False,
        blank=False,
        default=0
    )
    price_per_unit = models.DecimalField(
        blank=False,
        null=False,
        decimal_places=2,
        max_digits=10
    )
    order = models.ForeignKey(
        Orders,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f"Product Order: {self.product_name}"
