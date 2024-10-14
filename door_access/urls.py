#door_access/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_access, name='generate_access'),
    path('unlock/', views.unlock_door, name='unlock_door'),
]