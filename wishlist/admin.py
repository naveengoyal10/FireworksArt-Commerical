from django.contrib import admin
from .models import Wishlist, WishlistItem


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created', 'updated')
    search_fields = ('name', 'user__username', 'user__email')
    autocomplete_fields = ('user',)


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist', 'painting', 'quantity', 'created')
    search_fields = ('wishlist__name', 'painting__title')
    autocomplete_fields = ('wishlist', 'painting')
