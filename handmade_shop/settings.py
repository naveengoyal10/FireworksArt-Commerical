import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# load environment variables from .env in project root
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'CHANGE_ME_TO_A_SECURE_VALUE')

DEBUG = os.getenv('DEBUG', 'True') == 'True'



ALLOWED_HOSTS = os.getenv(    "ALLOWED_HOSTS",   ".vercel.app,localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [    "https://*.vercel.app",]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'shop',
    # Project apps
    'core',
    'accounts',
    'paintings',
    'cart',
    'orders',
    'payments',
    'dashboard',
    'reviews',
    'wishlist',
    'blog',
    # Authentication / social login
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.apple',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Optional storage backends are added conditionally below when configured

ROOT_URLCONF = 'handmade_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.seo_defaults',
            ],
        },
    },
]

WSGI_APPLICATION = 'handmade_shop.wsgi.application'

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
if DATABASE_URL.startswith("sqlite"):
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Allow overriding media URL/root from environment (useful when serving media from a separate host)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', str(BASE_DIR / 'media')))

# On Vercel serverless builds, the repository file system is read-only.
# Use /tmp/media for temporary writable storage when no persistent MEDIA_ROOT is configured.
if os.getenv('VERCEL') and not os.getenv('MEDIA_ROOT'):
    MEDIA_ROOT = Path('/tmp/media')

# Enable Cloudinary media storage when Cloudinary config is present.
cloudinary_url = os.getenv('CLOUDINARY_URL')
cloudinary_name = os.getenv('CLOUDINARY_CLOUD_NAME')
cloudinary_api_key = os.getenv('CLOUDINARY_API_KEY')
cloudinary_api_secret = os.getenv('CLOUDINARY_API_SECRET')

if cloudinary_url or cloudinary_name or cloudinary_api_key or cloudinary_api_secret:
    if cloudinary_url and not cloudinary_url.startswith('cloudinary://'):
        raise ImproperlyConfigured(
            "Invalid CLOUDINARY_URL. It must start with 'cloudinary://'"
        )

    import cloudinary

    if cloudinary_url:
        # Importing cloudinary already parses CLOUDINARY_URL into config.
        pass
    else:
        if not (cloudinary_name and cloudinary_api_key and cloudinary_api_secret):
            raise ImproperlyConfigured(
                "Cloudinary configuration requires CLOUDINARY_URL or all of "
                "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
            )
        cloudinary.config(
            cloud_name=cloudinary_name,
            api_key=cloudinary_api_key,
            api_secret=cloudinary_api_secret,
        )

    cloudinary_config = cloudinary.config()
    if not getattr(cloudinary_config, 'cloud_name', None):
        raise ImproperlyConfigured(
            "Cloudinary configuration is invalid: cloud_name is missing. "
            "Check CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET."
        )

    cloudinary_name = cloudinary_name or cloudinary_config.cloud_name
    cloudinary_api_key = cloudinary_api_key or cloudinary_config.api_key
    cloudinary_api_secret = cloudinary_api_secret or cloudinary_config.api_secret

    INSTALLED_APPS += [
        'cloudinary',
        'cloudinary_storage',
    ]
    CLOUDINARY_STORAGE = {
        'CLOUDINARY_URL': cloudinary_url,
        'CLOUD_NAME': cloudinary_name,
        'API_KEY': cloudinary_api_key,
        'API_SECRET': cloudinary_api_secret,
        'PREFIX': os.getenv('CLOUDINARY_PREFIX', ''),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    if 'MEDIA_URL' not in os.environ:
        MEDIA_URL = f'https://res.cloudinary.com/{cloudinary_name}/'

# Use S3 for media files when AWS_STORAGE_BUCKET_NAME is set in environment.
# If django-storages is unavailable, fallback to default local storage.
if os.getenv('AWS_STORAGE_BUCKET_NAME'):
    try:
        import storages  # noqa: F401
    except ImportError:
        AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', None)
        AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN') or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
        # If django-storages is not installed, keep default local storage and do not fail collectstatic.
    else:
        INSTALLED_APPS += [
            'storages',
        ]
        AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', None)
        AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN') or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        # Only override MEDIA_URL with S3 domain if user didn't explicitly set MEDIA_URL
        if 'MEDIA_URL' not in os.environ:
            MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# Third party service keys (set in .env)
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')

# Optional integrations
MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = os.getenv('MAILCHIMP_LIST_ID')
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SEO defaults
SITE_NAME = os.getenv('SITE_NAME', 'Handmade Paintings Shop')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
DEFAULT_META_TITLE = os.getenv('DEFAULT_META_TITLE', 'Handmade Paintings Shop - Original Handmade Artwork')
DEFAULT_META_DESCRIPTION = os.getenv('DEFAULT_META_DESCRIPTION', 'Discover original handmade paintings crafted by experienced artists. Shop unique artwork, explore custom art collections, and get inspired by distinctive designs for your home or office.')
DEFAULT_META_IMAGE = os.getenv('DEFAULT_META_IMAGE', f'{SITE_URL}/static/sample_images/logo.jpeg')
TWITTER_CREATOR = os.getenv('TWITTER_CREATOR', '@fireworkart')

# Email backend for development - prints emails to console
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

SOCIALACCOUNT_PROVIDERS = {}

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
APPLE_SECRET = os.getenv('APPLE_SECRET')
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS['google'] = {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        }
    }

if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
    SOCIALACCOUNT_PROVIDERS['facebook'] = {
        'APP': {
            'client_id': FACEBOOK_APP_ID,
            'secret': FACEBOOK_APP_SECRET,
            'key': '',
        }
    }

if APPLE_CLIENT_ID and APPLE_SECRET and APPLE_KEY_ID and APPLE_TEAM_ID:
    SOCIALACCOUNT_PROVIDERS['apple'] = {
        'APP': {
            'client_id': APPLE_CLIENT_ID,
            'secret': APPLE_SECRET,
            'key': APPLE_KEY_ID,
            'team': APPLE_TEAM_ID,
        }
    }
