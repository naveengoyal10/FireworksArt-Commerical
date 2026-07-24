from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'provider', 'amount', 'currency', 'status', 'created')
    list_filter = ('provider', 'status', 'created')
    search_fields = ('transaction_id', 'order__id')
    autocomplete_fields = ('order',)
    readonly_fields = ('created', 'updated')
