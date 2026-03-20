from rest_framework import viewsets, permissions
from .models import ImagenValidacion
from .serializers import ImagenValidacionSerializer


class EsAdminOSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class ImagenValidacionViewSet(viewsets.ModelViewSet):
    queryset = ImagenValidacion.objects.all().order_by('-fecha_subida')
    serializer_class = ImagenValidacionSerializer
    permission_classes = [EsAdminOSuperAdmin]

    def perform_create(self, serializer):
        serializer.save(subida_por=self.request.user)