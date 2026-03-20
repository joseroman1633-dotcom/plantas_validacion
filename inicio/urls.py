from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("acerca/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("home2/", views.home2, name="home2"),
    path("prueba/", views.prueba, name="prueba"),

    path("iniciar-prueba/", views.iniciar_prueba, name="iniciar_prueba"),
    path("prueba-publica/", views.iniciar_prueba_publica, name="iniciar_prueba_publica"),
    path("graficas-publicas/", views.graficas_publicas, name="graficas_publicas"),
]