from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('razorpay/<int:order_id>/', views.razorpay_checkout, name='razorpay_checkout'),
    path('razorpay/verify/', views.razorpay_verify, name='razorpay_verify'),
    path('stripe/<int:order_id>/', views.stripe_checkout, name='stripe_checkout'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
]
