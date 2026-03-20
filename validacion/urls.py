from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImagenValidacionViewSet

router = DefaultRouter()
router.register(r'imagenes', ImagenValidacionViewSet, basename='imagenes')

urlpatterns = [
    path("", include(router.urls)),
]