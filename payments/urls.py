from django.urls import path
from . import views

urlpatterns = [
    path('razorpay/verify/', views.razorpay_verify, name='payments_razorpay_verify'),
]
