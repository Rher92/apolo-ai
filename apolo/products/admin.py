from django.contrib import admin
from apolo.products.models import Products, Stock, StockTracer


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    pass


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    pass


@admin.register(StockTracer)
class StockTracerAdmin(admin.ModelAdmin):
    pass
