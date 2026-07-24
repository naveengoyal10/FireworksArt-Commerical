from django.contrib import admin
from .models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('active',)
    search_fields = ('name', 'slug')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('name', 'email', 'content', 'created', 'active')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'published_date')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('published', 'published_date', 'categories', 'tags')
    search_fields = ('title', 'excerpt', 'content')
    filter_horizontal = ('categories', 'tags')
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'active', 'created')
    list_filter = ('active', 'created')
    search_fields = ('name', 'email', 'content', 'post__title')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f'{queryset.count()} comment(s) approved.')
    approve_comments.short_description = 'Approve selected comments'
