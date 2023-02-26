from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='nordigen_index'),
    path('bank_list/', views.bank_list, name='nordigen_bank_list'),
    path('log_response/', views.log_response, name='nordigen_log_response'),
    path('test/', views.test, name='nordigen_test'),
]
