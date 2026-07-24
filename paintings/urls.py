from django.urls import path
from . import views

urlpatterns = [
    path('', views.painting_list, name='painting_list'),
    path('<slug:slug>/', views.painting_detail, name='painting_detail'),
]
