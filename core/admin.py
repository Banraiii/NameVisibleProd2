from django.contrib import admin

from .models import Item, OrderItem, Order, News, Payment

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(News)
admin.site.register(Payment)