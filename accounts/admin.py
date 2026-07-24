from django.contrib import admin
from .models import Profile, Address


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone', 'user__email')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'city', 'country', 'default')
    search_fields = ('user__username', 'line1', 'line2', 'city', 'country')
    list_filter = ('country', 'default')
    autocomplete_fields = ('user',)
