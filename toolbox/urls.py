from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_kontomierz/', views.load_kontomierz, name='load_kontomierz'),
    path('review_database/', views.review_database, name='review_database'),
]