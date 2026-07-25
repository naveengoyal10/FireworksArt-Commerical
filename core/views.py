import os

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from paintings.models import HeroSlider, Painting, Category
from .models import Testimonial, InstagramPost, NewsletterSubscriber
from .forms import ContactForm
from django.contrib import messages
from blog.models import Post
from django.db.models import F
from django.conf import settings
from django.http import JsonResponse


def home(request):
    # Prefer slides that have uploaded images to avoid showing the placeholder
    slides = HeroSlider.objects.filter(active=True).exclude(image='')
    featured = Painting.objects.filter(status='published', featured=True)[:8]
    categories = Category.objects.all()[:8]
    new_arrivals = Painting.objects.filter(status='published', new_arrival=True)[:8]
    best_sellers = Painting.objects.filter(status='published', bestseller=True)[:8]
    discounts = Painting.objects.filter(status='published').exclude(discount_price__isnull=True).filter(discount_price__lt=F('price'))[:8]
    testimonials = Testimonial.objects.filter(active=True)[:5]
    instagram = InstagramPost.objects.filter(active=True)[:8]
    recent_posts = Post.objects.filter(published=True).order_by('-published_date')[:3]

    # Optionally fetch Instagram feed if access token provided
    if settings.INSTAGRAM_ACCESS_TOKEN:
            try:
                import requests
                token = settings.INSTAGRAM_ACCESS_TOKEN
                # Basic fetch (may require updated API endpoints)
                resp = requests.get(f'https://graph.instagram.com/me/media?fields=id,caption,media_url&access_token={token}')
                data = resp.json()
                ig_items = []
                for item in data.get('data', [])[:8]:
                    ig_items.append({'image': item.get('media_url'), 'caption': item.get('caption', '')})
                instagram = ig_items
            except Exception:
                pass

    return render(request, 'core/home.html', {
        'slides': slides,
        'featured': featured,
        'categories': categories,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'discounts': discounts,
        'testimonials': testimonials,
        'instagram': instagram,
        'recent_posts': recent_posts,
        'meta_title': settings.DEFAULT_META_TITLE,
        'meta_description': settings.DEFAULT_META_DESCRIPTION,
        'meta_image': settings.DEFAULT_META_IMAGE,
        'og_type': 'website',
    })


def debug_cloudinary(request):
    if not (settings.DEBUG or os.getenv('CLOUDINARY_DEBUG') == 'True'):
        return JsonResponse({'error': 'Cloudinary debug endpoint disabled.'}, status=404)

    try:
        import cloudinary
        config = cloudinary.config()
        data = {
            'cloud_name': getattr(config, 'cloud_name', None),
            'api_key_set': bool(getattr(config, 'api_key', None)),
            'api_secret_set': bool(getattr(config, 'api_secret', None)),
            'default_file_storage': settings.DEFAULT_FILE_STORAGE,
            'media_url': settings.MEDIA_URL,
            'cloudinary_storage': getattr(settings, 'CLOUDINARY_STORAGE', {}),
            'cloudinary_url': os.getenv('CLOUDINARY_URL'),
            'cloudinary_cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
            'resolved_cloudinary_config': {
                'cloud_name': getattr(config, 'cloud_name', None),
                'secure': getattr(config, 'secure', None),
                'cdn_subdomain': getattr(config, 'cdn_subdomain', None),
                'secure_distribution': getattr(config, 'secure_distribution', None),
                'private_cdn': getattr(config, 'private_cdn', None),
            },
        }
    except Exception as exc:
        data = {'error': str(exc)}
    return JsonResponse(data)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            subject = f"Contact form: {cleaned['subject']}"
            message = f"Name: {cleaned['name']}\nEmail: {cleaned['email']}\n\n{cleaned['message']}"
            from_email = cleaned['email']
            recipient = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
            try:
                send_mail(subject, message, from_email, [recipient], fail_silently=False)
                messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
                return redirect('contact')
            except Exception:
                messages.error(request, 'Unable to send your message at this time. Please try again later.')
    else:
        form = ContactForm()

    business_info = {
        'address': '123 Art Lane, Creative City, Country',
        'phone': '+1 555 123 456',
        'email': 'support@fireworkart.com',
        'hours': 'Mon - Fri: 9am - 6pm',
    }
    social_links = [
        {'name': 'Instagram', 'url': 'https://instagram.com/fireworkart'},
        {'name': 'Facebook', 'url': 'https://facebook.com/fireworkart'},
        {'name': 'Twitter', 'url': 'https://twitter.com/fireworkart'},
        {'name': 'Pinterest', 'url': 'https://pinterest.com/fireworkart'},
    ]
    return render(request, 'core/contact.html', {
        'form': form,
        'business_info': business_info,
        'social_links': social_links,
        'meta_title': 'Contact Handmade Paintings',
        'meta_description': 'Get in touch with Handmade Paintings for orders, wholesale inquiries, or general questions.',
        'meta_image': settings.DEFAULT_META_IMAGE,
        'og_type': 'website',
    })


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                # If Mailchimp configured, try to add subscriber
                try:
                    from django.conf import settings
                    if settings.MAILCHIMP_API_KEY and settings.MAILCHIMP_LIST_ID:
                        import requests, hashlib
                        api_key = settings.MAILCHIMP_API_KEY
                        list_id = settings.MAILCHIMP_LIST_ID
                        dc = api_key.split('-')[-1]
                        url = f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members'
                        payload = {'email_address': email, 'status': 'subscribed'}
                        resp = requests.post(url, auth=('anystring', api_key), json=payload)
                        if resp.status_code in (200, 201):
                            messages.success(request, 'Thanks for subscribing!')
                        else:
                            messages.success(request, 'Subscribed locally (Mailchimp API call failed).')
                    else:
                        messages.success(request, 'Thanks for subscribing!')
                except Exception:
                    messages.success(request, 'Subscribed locally (Mailchimp error).')
            else:
                messages.info(request, 'You are already subscribed.')
        else:
            messages.error(request, 'Please provide a valid email.')
    return redirect('home')
