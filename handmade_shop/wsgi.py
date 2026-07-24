import os
import core.django_patches  # noqa: F401
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handmade_shop.settings')
application = get_wsgi_application()
