from django.contrib import admin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewImageInline]
    list_display = ('painting', 'user', 'rating', 'active', 'created')
    list_filter = ('active', 'rating', 'created')
    search_fields = ('painting__title', 'user__username', 'title', 'content')
    readonly_fields = ('created',)
