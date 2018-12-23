from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:account_id>/', views.account_detail, name='account_detail'),
    path('bank/<int:bank_id>/', views.bank_detail, name='bank_detail'),
]