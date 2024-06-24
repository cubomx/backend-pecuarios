from django.urls import path

from . import views

urlpatterns = [
    path('compra', views.compra, name='registo de compra')

]