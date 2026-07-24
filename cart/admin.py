from django.contrib import admin
from .models import Cart, CartItem, Coupon


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'coupon', 'active', 'created', 'updated')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('user__username', 'session_key', 'coupon__code')
    autocomplete_fields = ('user', 'coupon')
    readonly_fields = ('created', 'updated')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'painting', 'quantity', 'price', 'subtotal', 'created')
    list_filter = ('created',)
    search_fields = ('painting__title', 'cart__session_key', 'cart__user__username')
    autocomplete_fields = ('cart', 'painting')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'is_valid', 'active', 'usage_count', 'created')
    list_filter = ('active', 'discount_type', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    readonly_fields = ('usage_count', 'created')
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'description')
        }),
        ('Discount', {
            'fields': ('discount_type', 'value', 'min_purchase', 'max_discount')
        }),
        ('Validity', {
            'fields': ('active', 'valid_from', 'valid_to')
        }),
        ('Usage', {
            'fields': ('usage_limit', 'usage_count', 'created'),
        }),
    )
