from django.db import models


class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name}'


class InstagramPost(models.Model):
    image = models.ImageField(upload_to='instagram/', blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.caption or f'IG {self.pk}'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    scheduled_send = models.DateTimeField(null=True, blank=True)
    sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.subject

    def send(self):
        from django.conf import settings
        from django.core.mail import send_mail
        from django.utils import timezone

        subscribers = NewsletterSubscriber.objects.values_list('email', flat=True)
        if not subscribers:
            return 0

        from_email = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
        sent_count = 0

        for email in subscribers:
            send_mail(self.subject, self.body, from_email, [email], fail_silently=False)
            sent_count += 1

        self.sent = True
        self.sent_date = timezone.now()
        self.save(update_fields=['sent', 'sent_date'])
        return sent_count


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default='Handmade Paintings Shop')
    default_meta_title = models.CharField(max_length=255, blank=True)
    default_meta_description = models.CharField(max_length=255, blank=True)
    default_meta_image = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_active(cls):
        return cls.objects.order_by('-updated').first()


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Contact from {self.name} - {self.subject}'
