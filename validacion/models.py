import base64
import mimetypes

from django.db import models
from django.contrib.auth.models import User
from inicio.models import ParticipantePublico


class ImagenValidacion(models.Model):
    TIPO_CHOICES = [
        ("IA", "Imagen generada por IA"),
        ("NO_IA", "Sintética"),
    ]

    nombre = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="imagenes_validacion/")
    imagen_base64 = models.TextField(blank=True, null=True)
    tipo_origen = models.CharField(max_length=10, choices=TIPO_CHOICES)
    seleccionada = models.BooleanField(default=False)
    subida_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.tipo_origen}"

    def generar_imagen_base64(self):
        if not self.imagen:
            return None

        try:
            self.imagen.open("rb")
            contenido = self.imagen.read()

            mime_type, _ = mimetypes.guess_type(self.imagen.name)
            if not mime_type:
                mime_type = "image/jpeg"

            imagen_codificada = base64.b64encode(contenido).decode("utf-8")
            return f"data:{mime_type};base64,{imagen_codificada}"
        except Exception:
            return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        nueva_base64 = self.generar_imagen_base64()

        if nueva_base64 and self.imagen_base64 != nueva_base64:
            self.imagen_base64 = nueva_base64
            super().save(update_fields=["imagen_base64"])


class SesionPrueba(models.Model):
    DESTINATARIO_CHOICES = [
        ("DR_JORGE", "Dr. Jorge"),
        ("LUCIANO", "Luciano"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    finalizada = models.BooleanField(default=False)
    destinatario = models.CharField(
        max_length=20,
        choices=DESTINATARIO_CHOICES,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Sesión #{self.id} - {self.usuario.username}"


class PruebaImagenRespuesta(models.Model):
    RESPUESTA_CHOICES = [
        ("IA", "IA"),
        ("NO_IA", "SINTÉTICA"),
    ]

    sesion = models.ForeignKey(
        SesionPrueba,
        on_delete=models.CASCADE,
        related_name="respuestas",
        null=True,
        blank=True
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ForeignKey(ImagenValidacion, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=20, choices=RESPUESTA_CHOICES)
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.imagen.nombre} - {self.respuesta}"


class SesionPruebaPublica(models.Model):
    DESTINATARIO_CHOICES = [
        ("DR_JORGE", "Dr. Jorge"),
        ("LUCIANO", "Luciano"),
    ]

    participante = models.ForeignKey(
        ParticipantePublico,
        on_delete=models.CASCADE,
        related_name="sesiones_publicas",
        null=True,
        blank=True
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    finalizada = models.BooleanField(default=False)
    destinatario = models.CharField(
        max_length=20,
        choices=DESTINATARIO_CHOICES,
        blank=True,
        null=True
    )

    def __str__(self):
        if self.participante:
            return f"Sesión pública #{self.id} - {self.participante.nombre}"
        return f"Sesión pública #{self.id}"


class PruebaImagenRespuestaPublica(models.Model):
    RESPUESTA_CHOICES = [
        ("IA", "IA"),
        ("NO_IA", "SINTÉTICA"),
    ]

    sesion = models.ForeignKey(
        SesionPruebaPublica,
        on_delete=models.CASCADE,
        related_name="respuestas",
        null=True,
        blank=True
    )
    participante = models.ForeignKey(
        ParticipantePublico,
        on_delete=models.CASCADE,
        related_name="respuestas_publicas",
        null=True,
        blank=True
    )
    imagen = models.ForeignKey(ImagenValidacion, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=20, choices=RESPUESTA_CHOICES)
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre = self.participante.nombre if self.participante else "Participante público"
        return f"{nombre} - {self.imagen.nombre} - {self.respuesta}"
