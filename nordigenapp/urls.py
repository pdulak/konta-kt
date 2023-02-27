from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='nordigen_index'),
    path('bank_list/', views.bank_list, name='nordigen_bank_list'),
    path('log_response/', views.log_response, name='nordigen_log_response'),
    path('test/', views.test, name='nordigen_test'),
    path('force_token_refresh/', views.force_token_refresh, name='nordigen_force_token_refresh'),
    path('connect_bank/<str:institution_id>/', views.connect_bank, name='nordigen_connect_bank'),
    path('account_details/<str:account_id>/', views.account_details, name='nordigen_account_details'),
    path('account_transactions/<str:account_id>/', views.account_transactions, name='nordigen_account_transactions'),
    path('assign_account/<int:kontakt_account_id>/<str:nordigen_account_id>/<str:iban>/', views.assign_account,
         name='nordigen_assign_account'),
]
