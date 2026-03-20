import base64

from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path

from .forms import MultipleImageUploadForm
from .models import ImagenValidacion, SesionPrueba, PruebaImagenRespuesta


@admin.register(ImagenValidacion)
class ImagenValidacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'tipo_origen',
        'seleccionada',
        'subida_por',
        'fecha_subida',
        'activa',
    )

    list_filter = (
        'tipo_origen',
        'seleccionada',
        'activa',
        'fecha_subida',
    )

    search_fields = (
        'nombre',
        'subida_por__username',
    )

    exclude = ('imagen_base64',)

    change_list_template = "admin/validacion/imagenvalidacion/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'carga-multiple/',
                self.admin_site.admin_view(self.carga_multiple_view),
                name='validacion_imagenvalidacion_carga_multiple'
            ),
        ]
        return custom_urls + urls

    def carga_multiple_view(self, request):
        if not self.has_add_permission(request):
            messages.error(request, "No tienes permisos para agregar imágenes.")
            return redirect("..")

        if request.method == "POST":
            form = MultipleImageUploadForm(request.POST, request.FILES)

            if form.is_valid():
                files = form.cleaned_data["imagenes"]
                tipo_origen = form.cleaned_data["tipo_origen"]
                seleccionada = form.cleaned_data["seleccionada"]
                activa = form.cleaned_data["activa"]

                total = 0

                for archivo in files:
                    nombre_base = archivo.name.rsplit(".", 1)[0]

                    imagen_base64 = None
                    if seleccionada:
                        contenido = archivo.read()
                        imagen_base64 = base64.b64encode(contenido).decode("utf-8")
                        archivo.seek(0)

                    ImagenValidacion.objects.create(
                        nombre=nombre_base,
                        imagen=archivo,
                        imagen_base64=imagen_base64,
                        tipo_origen=tipo_origen,
                        seleccionada=seleccionada,
                        activa=activa,
                        subida_por=request.user,
                    )
                    total += 1

                self.message_user(
                    request,
                    f"Se cargaron correctamente {total} imágenes.",
                    level=messages.SUCCESS
                )
                return redirect("../")
        else:
            form = MultipleImageUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": "Carga múltiple de imágenes",
        }

        return render(
            request,
            "admin/validacion/imagenvalidacion/carga_multiple.html",
            context,
        )


@admin.register(SesionPrueba)
class SesionPruebaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'destinatario',
        'finalizada',
        'fecha_inicio',
        'fecha_fin',
    )

    list_filter = (
        'destinatario',
        'finalizada',
        'fecha_inicio',
    )

    search_fields = (
        'usuario__username',
    )


@admin.register(PruebaImagenRespuesta)
class PruebaImagenRespuestaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sesion',
        'usuario',
        'imagen',
        'respuesta',
        'es_correcta',
        'fecha_respuesta',
    )

    list_filter = (
        'respuesta',
        'es_correcta',
        'fecha_respuesta',
    )

    search_fields = (
        'usuario__username',
        'imagen__nombre',
    )