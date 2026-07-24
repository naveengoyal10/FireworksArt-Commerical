from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:painting_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:painting_id>/', views.remove_from_cart, name='cart_remove'),
    path('update/<int:painting_id>/', views.update_quantity, name='update_quantity'),
    path('save/<int:painting_id>/', views.save_for_later, name='save_for_later'),
    path('move-to-cart/<int:painting_id>/', views.move_to_cart, name='move_to_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
]
