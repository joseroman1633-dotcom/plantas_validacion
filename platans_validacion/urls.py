from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from inicio import views as inicio_views

urlpatterns = [
    path("admin/info/", inicio_views.admin_info, name="admin_info"),
    path("admin/graficas/", inicio_views.admin_graficas, name="admin_graficas"),
    path("admin/graficas-publicas/", inicio_views.admin_graficas_publicas, name="admin_graficas_publicas"),

    path("salir/", inicio_views.salir, name="salir"),

    path("admin/", admin.site.urls),

    path("", include("inicio.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("validacion.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)