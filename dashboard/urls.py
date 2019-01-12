from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('j_transactions/', views.j_transactions, name='j_transactions'),
]
