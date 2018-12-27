from django.urls import path

from . import views

urlpatterns = [
    path('monthly_review/', views.monthly_review, name='monthly_review'),
    path('', views.index, name='index'),
]