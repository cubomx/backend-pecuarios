from django.urls import path

from . import views

urlpatterns = [
    path('compra', views.compra, name='registo de compra'),
    path('empadre', views.empadre, name='registro de empadre'),
    path('nacimiento', views.nacimiento, name='registro de nacimiento')
]