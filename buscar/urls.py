from django.urls import path

from . import views

urlpatterns = [
    path('vacas', views.getVacas, name='obtener vacas'),
    path('partos', views.getPartos, name='obtener partos')
]