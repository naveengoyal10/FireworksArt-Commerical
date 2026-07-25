from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Painting(models.Model):
    ORIENTATION_CHOICES = [
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape'),
        ('square', 'Square'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    categories = models.ManyToManyField(Category, related_name='paintings', blank=True)
    artist_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    story = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    medium = models.CharField(max_length=200, blank=True)
    size = models.CharField(max_length=100, blank=True)
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, blank=True)
    frame_option = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    featured_image = models.ImageField(upload_to='paintings/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    show_in_shop = models.BooleanField(default=True, help_text='Show this painting on the shop page')
    featured = models.BooleanField(default=False)
    bestseller = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('painting_detail', args=[self.slug])

    @property
    def average_rating(self):
        avg = self.reviews.filter(active=True).aggregate(avg=Avg('rating'))['avg']
        return avg if avg is not None else None


class PaintingImage(models.Model):
    painting = models.ForeignKey(Painting, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='paintings/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Image for {self.painting.title}'


class HeroSlider(models.Model):
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f'Hero {self.pk}'
