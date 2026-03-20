from django.contrib import admin
from django.urls import path
from .views import admin_info, admin_graficas, admin_graficas_publicas
from .models import PerfilUsuario


admin.site.site_header = "Platans Validation System"
admin.site.site_title = "Platans Admin"
admin.site.index_title = "Panel de administración"


_original_get_urls = admin.site.get_urls


def get_urls():
    urls = _original_get_urls()
    custom_urls = [
        path("info/", admin.site.admin_view(admin_info), name="admin_info"),
        path("graficas/", admin.site.admin_view(admin_graficas), name="admin_graficas"),
        path("graficas-publicas/", admin.site.admin_view(admin_graficas_publicas), name="admin_graficas_publicas"),
    ]
    return custom_urls + urls


admin.site.get_urls = get_urls


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "edad",
        "sexo",
        "rol",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
    )

    list_filter = (
        "sexo",
        "rol",
    )