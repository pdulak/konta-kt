from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('load_kontomierz/', views.load_kontomierz, name='load_kontomierz'), - no longer in use
    path('load_mbank/', views.load_mbank, name='load_mbank'),
    path('load_alior/', views.load_alior, name='load_alior'),
    path('review_database/', views.review_database, name='review_database'),
    path('adjust_nbp/', views.adjust_nbp, name='adjust_nbp'),
    path('cleanup/', views.do_cleanup, name='cleanup')
]