"""
URL configuration for pecuarios project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('api/buscar/', include('buscar.urls')),
    path('api/register/', include('register.urls')),
    path('api/addRancho', views.addRancho, name='Agregar rancho'),
    path('api/addLote', views.addLote, name='Agregar lote'),
    path('api/getRanchos', views.getRanchos, name='Obtener ranchos'),
    path('api/getLotes', views.getLotes, name='Obtener lotes por rancho'),
]
