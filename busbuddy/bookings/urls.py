from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_buses, name='search_buses'),
]
