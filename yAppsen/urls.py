"""yAppsen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ObtenerRamos/', ObtenerRamos, name='ObtenerRamos'),
    path('', index, name='index'),
    path('registro/', registro, name='registro'),
    path('contacto/', contacto, name='contacto'),
    path('login/', IniciarSesion, name='IniciarSesion'),
    path('logout/', CerrarSesion, name='CerrarSesion'),
    path('ramos/inscribir/', InscribirRamos, name='InscribirRamos'),
    path('horario/clases/inscribir', InscribirClases, name='InscribirClases'),
    path('HorasEstudio/generar/seleccionar', Seleccionar, name='Seleccionar'),
    path('HorasEstudio/generar/automatico', pref_Automatico, name='Automatico'),
    path('HorasEstudio/generar/manual', manual, name='Manual'),
    path('inicio/', principal, name='principal'),
]