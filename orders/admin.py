from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('created',)
    fields = ('painting', 'price', 'quantity', 'created')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total', 'status', 'payment_status', 'payment_method', 'created')
    list_filter = ('status', 'payment_status', 'payment_method', 'created', 'updated')
    search_fields = ('id', 'full_name', 'email', 'phone')
    readonly_fields = ('created', 'updated', 'razorpay_order_id', 'razorpay_payment_id', 'stripe_payment_intent')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'created', 'updated')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country')
        }),
        ('Shipping Address', {
            'fields': ('same_as_billing', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Order Details', {
            'fields': ('subtotal', 'discount', 'tax', 'shipping_cost', 'total', 'coupon_code', 'status', 'notes')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id', 'stripe_payment_intent'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'painting', 'quantity', 'price', 'get_subtotal', 'created')
    list_filter = ('order__created', 'created')
    search_fields = ('order__id', 'painting__title')
    readonly_fields = ('created',)
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal}"
    get_subtotal.short_description = 'Subtotal'
