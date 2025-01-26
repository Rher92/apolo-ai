from slugify import slugify

from django.db import models

from apolo.utils.models import MetaModel


class Products(MetaModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False
    )
    slug_name = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False
    )

    def save(self, *args, **kwargs):
        if not self.slug_name:
            self.slug_name = slugify(self.name, separator="_")
        self.original_pk = self.pk
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.slug_name}"


class Stock(MetaModel):
    quantity = models.IntegerField(
        blank=False,
        null=False,
        default=0,
    )
    price_per_unit = models.DecimalField(
        blank=False,
        null=False,
        decimal_places=2,
        max_digits=10
    )    
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name='stock'
    )


class StockTracer(MetaModel):
    class Flows(models.TextChoices):
        IN = "IN", ("Stock inflow")
        OUT = "OUT", ("Stock outflow")

    product = models.ForeignKey(
        Products,
        on_delete=models.DO_NOTHING
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.DO_NOTHING
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
    flow = models.CharField(
        max_length=3,
        choices=Flows,
        default=Flows.IN,
    )
    
    def _update_stock(self):
        stock = Stock.objects.get(pk=self.stock.pk)
        quantity = stock.quantity
        if self.flow == self.Flows.IN:
            stock.quantity = quantity + self.quantity
        elif self.flow == self.Flows.OUT:
            stock.quantity = quantity - self.quantity
        stock.save(update_fields=["quantity"])
    
    def save(self, *args, **kwargs):
        update_stock = True if not self.pk else False 
        if update_stock:
            super().save(*args, **kwargs)
            self._update_stock()
