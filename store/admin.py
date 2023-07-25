from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count

from .models import Category, Comment, Order, Product


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_and_10 = '3<=10'
    MORE_THAN_10 = '>10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'High'),
            (InventoryFilter.BETWEEN_3_and_10, 'Medium'),
            (InventoryFilter.MORE_THAN_10, 'OK'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == InventoryFilter.BETWEEN_3_and_10:
            return queryset.filter(inventory__range=(3, 10))
        if self.value() == InventoryFilter.MORE_THAN_10:
            return queryset.filter(inventory__gt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory', 'unit_price', 'inventory_status', 'product_category']
    list_per_page = 10
    list_editable = ['unit_price']
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter]

    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 50:
            return 'High'
        return 'Medium'
    
    
    @admin.display(ordering='category__title')
    def product_category(self, product):
        return product.category.title
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status', ]
    list_editable = ['status']
    list_per_page = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'datetime_created', 'num_of_items']
    list_editable = ['status']
    list_per_page = 10
    ordering = ['-datetime_created']

    def get_queryset(self, request):
        return super() \
                .get_queryset(request) \
                .prefetch_related('items') \
                .annotate(
                    items_count=Count('items')
                )

    @admin.display(ordering='items_count')
    def num_of_items(self, order):
        return order.items_count

admin.site.register(Category)
