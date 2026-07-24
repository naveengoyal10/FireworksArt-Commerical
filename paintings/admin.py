from django.contrib import admin
from .models import Category, Painting, PaintingImage, HeroSlider


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)


class PaintingImageInline(admin.TabularInline):
    model = PaintingImage
    extra = 1


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'price', 'stock', 'status', 'featured')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'featured', 'bestseller', 'new_arrival', 'categories')
    search_fields = ('title', 'artist_name', 'sku')
    inlines = [PaintingImageInline]


@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'active')
