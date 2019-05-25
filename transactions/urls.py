from django.urls import path

from . import views

urlpatterns = [
    path('monthly_review/', views.monthly_review, name='monthly_review'),
    path('account_balance/', views.account_balance, name='account_balance'),
    path('transactions_review/', views.transactions_review, name='transactions_review'),
    path('change_relevancy/', views.change_relevancy, name='change_relevancy'),
    path('change_approval/', views.change_approval, name='change_approval'),
    path('months/', views.months, name='months'),
    path('save/', views.save, name='save'),
    path('', views.index, name='index'),
]