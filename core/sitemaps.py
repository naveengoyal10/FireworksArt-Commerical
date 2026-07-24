from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from paintings.models import Painting


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['home', 'contact']

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Post.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.published_date


class PaintingSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Painting.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated
