import json
from django.conf import settings


def seo_defaults(request):
    canonical_url = request.build_absolute_uri(request.path)
    site_settings = None
    try:
        from .models import SiteSettings
        site_settings = SiteSettings.get_active()
    except Exception:
        site_settings = None

    if site_settings:
        default_meta_title = site_settings.default_meta_title or getattr(settings, 'DEFAULT_META_TITLE', '')
        default_meta_description = site_settings.default_meta_description or getattr(settings, 'DEFAULT_META_DESCRIPTION', '')
        default_meta_image = site_settings.default_meta_image or getattr(settings, 'DEFAULT_META_IMAGE', '')
        site_name = site_settings.site_name or getattr(settings, 'SITE_NAME', '')
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    else:
        default_meta_title = getattr(settings, 'DEFAULT_META_TITLE', '')
        default_meta_description = getattr(settings, 'DEFAULT_META_DESCRIPTION', '')
        default_meta_image = getattr(settings, 'DEFAULT_META_IMAGE', '')
        site_name = getattr(settings, 'SITE_NAME', '')
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')

    return {
        'site_name': site_name,
        'site_url': site_url,
        'default_meta_title': default_meta_title,
        'default_meta_description': default_meta_description,
        'default_meta_image': default_meta_image,
        'twitter_creator': getattr(settings, 'TWITTER_CREATOR', ''),
        'canonical_url': canonical_url,
        'google_social_login_enabled': bool(getattr(settings, 'GOOGLE_CLIENT_ID', '') and getattr(settings, 'GOOGLE_CLIENT_SECRET', '')),
        'facebook_social_login_enabled': bool(getattr(settings, 'FACEBOOK_APP_ID', '') and getattr(settings, 'FACEBOOK_APP_SECRET', '')),
        'apple_social_login_enabled': bool(getattr(settings, 'APPLE_CLIENT_ID', '') and getattr(settings, 'APPLE_SECRET', '') and getattr(settings, 'APPLE_KEY_ID', '') and getattr(settings, 'APPLE_TEAM_ID', '')),
        'default_structured_data': json.dumps({
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            'url': site_url,
            'name': site_name,
            'publisher': {
                '@type': 'Organization',
                'name': site_name,
            }
        }),
    }
