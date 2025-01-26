from django.contrib import admin

from apolo.orders.models import Orders, ProductOrders



@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductOrders)
class StockAdmin(admin.ModelAdmin):
    pass

