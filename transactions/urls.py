from django.urls import path

from . import views

urlpatterns = [
    path('monthly_review/', views.monthly_review, name='monthly_review'),
    path('account_balance/', views.account_balance, name='account_balance'),
    path('transactions_review/', views.transactions_review, name='transactions_review'),
    path('change_relevancy/', views.change_relevancy, name='change_relevancy'),
    path('months/', views.months, name='months'),
    path('', views.index, name='index'),
]