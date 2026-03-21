from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ImagenValidacion,
    SesionPrueba,
    PruebaImagenRespuesta,
    SesionPruebaPublica,
    PruebaImagenRespuestaPublica,
)


@admin.register(ImagenValidacion)
class ImagenValidacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "preview_imagen",
        "imagen",
        "tipo_origen",
        "seleccionada",
        "activa",
    )
    search_fields = ("nombre", "imagen")
    list_filter = ("tipo_origen", "activa", "seleccionada")
    readonly_fields = ("preview_imagen", "fecha_subida")
    fields = (
        "nombre",
        "imagen",
        "preview_imagen",
        "tipo_origen",
        "seleccionada",
        "activa",
        "subida_por",
        "imagen_base64",
        "fecha_subida",
    )

    def save_model(self, request, obj, form, change):
        if not obj.subida_por:
            obj.subida_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Vista previa")
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="/static/{}" style="max-height:120px;border-radius:8px;border:1px solid #ccc;padding:4px;" />',
                obj.imagen
            )
        if obj.imagen_base64:
            return format_html(
                '<img src="data:image/jpeg;base64,{}" style="max-height:120px;border-radius:8px;border:1px solid #ccc;padding:4px;" />',
                obj.imagen_base64
            )
        return "Sin imagen"


@admin.register(SesionPrueba)
class SesionPruebaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "fecha_inicio", "fecha_fin", "finalizada", "destinatario")
    list_filter = ("finalizada", "destinatario")


@admin.register(PruebaImagenRespuesta)
class PruebaImagenRespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "imagen", "respuesta", "es_correcta", "fecha_respuesta")
    list_filter = ("respuesta", "es_correcta")


@admin.register(SesionPruebaPublica)
class SesionPruebaPublicaAdmin(admin.ModelAdmin):
    list_display = ("id", "participante", "fecha_inicio", "fecha_fin", "finalizada", "destinatario")
    list_filter = ("finalizada", "destinatario")


@admin.register(PruebaImagenRespuestaPublica)
class PruebaImagenRespuestaPublicaAdmin(admin.ModelAdmin):
    list_display = ("id", "participante", "imagen", "respuesta", "es_correcta", "fecha_respuesta")
    list_filter = ("respuesta", "es_correcta")
