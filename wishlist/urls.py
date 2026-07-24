from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_view, name='wishlist_view'),
    path('add/<int:painting_id>/', views.add_to_wishlist, name='wishlist_add'),
    path('remove/<int:painting_id>/', views.remove_from_wishlist, name='wishlist_remove'),
    path('move-to-cart/<int:painting_id>/', views.move_to_cart, name='move_to_cart'),
]
