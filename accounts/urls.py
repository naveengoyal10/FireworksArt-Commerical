from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='accounts_register'),
    path('profile/', views.profile, name='accounts_profile'),
    path('profile/edit/', views.edit_profile, name='accounts_edit_profile'),
    path('addresses/', views.address_list, name='accounts_address_list'),
    path('addresses/add/', views.address_add, name='accounts_address_add'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='accounts_address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='accounts_address_delete'),
]
