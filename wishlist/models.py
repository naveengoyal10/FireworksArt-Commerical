from django.db import models


class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=150, default='My Wishlist')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} ({self.user.username if self.user else "Guest"})'


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    painting = models.ForeignKey('paintings.Painting', related_name='wishlist_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        unique_together = ('wishlist', 'painting')

    def __str__(self):
        return f'{self.quantity} × {self.painting.title}'
