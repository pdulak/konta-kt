from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cleanup_database/', views.cleanup_database, name='cleanup_database'),
    path('initialize_database/', views.initialize_database, name='initialize_database'),
]