from django.db import models
from django.contrib.auth import get_user_model
from paintings.models import Painting


class Review(models.Model):
    painting = models.ForeignKey(Painting, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name='painting_reviews', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.painting.title} review by {self.user or 'Guest'}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_images/')
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for review {self.review.id}"
