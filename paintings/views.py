import json
from django.shortcuts import render, get_object_or_404
from .models import Painting


def painting_list(request):
    paintings = Painting.objects.filter(status='published')
    return render(request, 'paintings/painting_list.html', {'paintings': paintings})


def painting_detail(request, slug):
    painting = get_object_or_404(Painting, slug=slug, status='published')
    review_list = painting.reviews.filter(active=True).select_related('user')[:4]
    related_paintings = Painting.objects.filter(
        categories__in=painting.categories.all(),
        status='published'
    ).exclude(pk=painting.pk).distinct()[:4]
    active_review_count = painting.reviews.filter(active=True).count()
    rounded_rating = int(round(painting.average_rating)) if painting.average_rating else 0

    structured_data = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': painting.title,
        'image': [painting.featured_image.url] if painting.featured_image else [],
        'description': painting.description,
        'sku': painting.sku,
        'offers': {
            '@type': 'Offer',
            'priceCurrency': 'INR',
            'price': str(painting.discount_price or painting.price),
            'availability': 'https://schema.org/InStock' if painting.stock > 0 else 'https://schema.org/OutOfStock',
            'url': request.build_absolute_uri(painting.get_absolute_url()),
        }
    }
    context = {
        'painting': painting,
        'review_list': review_list,
        'related_paintings': related_paintings,
        'active_review_count': active_review_count,
        'rounded_rating': rounded_rating,
        'meta_title': painting.title,
        'meta_description': painting.description[:160] if painting.description else f'Handmade painting by {painting.artist_name or "Unknown Artist"}.',
        'meta_image': painting.featured_image.url if painting.featured_image else None,
        'og_type': 'product',
        'structured_data': json.dumps(structured_data),
    }
    return render(request, 'paintings/painting_detail.html', context)
