from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import LoginView
from accounts.forms import LoginForm
from accounts.views import logout_confirm
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import PaintingSitemap, StaticViewSitemap
from core import views as core_views

sitemaps = {
    'static': StaticViewSitemap,
    'paintings': PaintingSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('debug/cloudinary/', core_views.debug_cloudinary, name='debug_cloudinary'),
    path('', include('core.urls')),
    # convenience shortcut: /register/ -> accounts register view
    path('register/', RedirectView.as_view(pattern_name='accounts_register', permanent=False)),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html', authentication_form=LoginForm), name='login'),
    path('accounts/logout/', logout_confirm, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('paintings/', include('paintings.urls')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('wishlist/', include(('wishlist.urls', 'wishlist'), namespace='wishlist')),
    path('shop/', include('shop.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
