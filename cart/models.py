from decimal import Decimal
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
    ]

    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage value (0-100) or fixed amount")
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum purchase amount to apply coupon")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum discount amount (optional)")
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited usage")
    usage_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


class Cart(models.Model):
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Cart {self.id} - {self.user or self.session_key or "Guest"}'

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_discount(self):
        if self.coupon and self.coupon.is_valid:
            if self.coupon.discount_type == 'percentage':
                discount = self.subtotal * (self.coupon.value / 100)
            else:
                discount = min(self.coupon.value, self.subtotal)
            if self.coupon.max_discount:
                discount = min(discount, self.coupon.max_discount)
            return discount
        return 0

    @property
    def tax(self):
        return (self.subtotal - self.total_discount) * Decimal('0.10')

    @property
    def shipping(self):
        return Decimal('10.00') if self.subtotal - self.total_discount > 0 else Decimal('0.00')

    @property
    def total(self):
        return self.subtotal - self.total_discount + self.tax + self.shipping


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    painting = models.ForeignKey('paintings.Painting', related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        unique_together = ('cart', 'painting')

    def __str__(self):
        return f'{self.quantity} x {self.painting.title}'

    @property
    def subtotal(self):
        return self.price * self.quantity
