import os
import random
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseForbidden

from .forms import RegistroForm, ParticipantePublicoForm
from validacion.models import (
    ImagenValidacion,
    PruebaImagenRespuesta,
    SesionPrueba,
    SesionPruebaPublica,
    PruebaImagenRespuestaPublica,
)


# =========================
# VISTAS BÁSICAS
# =========================

def home(request):
    return render(request, "inicio/home.html")


def about(request):
    return render(request, "inicio/acerca.html")


def prueba(request):
    return render(request, "inicio/prueba.html")


def salir(request):
    logout(request)
    return redirect("home")


@login_required
def home2(request):
    return render(request, "inicio/home2.html")


@staff_member_required
def admin_info(request):
    return render(request, "admin/info.html")


# =========================
# 🔐 CREAR SUPERUSUARIO (RENDER)
# =========================

def bootstrap_superuser(request):
    token = request.GET.get("token")
    expected = os.getenv("BOOTSTRAP_TOKEN", "")

    if not expected or token != expected:
        return HttpResponseForbidden("No autorizado")

    username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "Jorge")
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "jorge@example.com")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "B4E965B14F")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    if created:
        return HttpResponse("Superusuario creado correctamente.")
    return HttpResponse("Superusuario actualizado correctamente.")


# =========================
# PRUEBA PRIVADA
# =========================

@login_required
def iniciar_prueba(request):
    if "prueba_ids" not in request.session:
        imagenes_ids = list(
            ImagenValidacion.objects.filter(activa=True).values_list("id", flat=True)
        )

        if not imagenes_ids:
            return render(request, "inicio/iniciar_prueba.html", {
                "sin_imagenes": True
            })

        random.shuffle(imagenes_ids)
        prueba_ids = imagenes_ids[:10]

        sesion = SesionPrueba.objects.create(usuario=request.user)

        request.session["prueba_ids"] = prueba_ids
        request.session["prueba_index"] = 0
        request.session["sesion_prueba_id"] = sesion.id

    prueba_ids = request.session.get("prueba_ids", [])
    prueba_index = request.session.get("prueba_index", 0)
    sesion_id = request.session.get("sesion_prueba_id")

    if not sesion_id:
        return redirect("iniciar_prueba")

    sesion = get_object_or_404(SesionPrueba, id=sesion_id, usuario=request.user)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "responder":
            imagen_id = request.POST.get("imagen_id")
            respuesta = request.POST.get("respuesta")

            if imagen_id and respuesta:
                imagen = get_object_or_404(ImagenValidacion, id=imagen_id)
                es_correcta = imagen.tipo_origen == respuesta

                PruebaImagenRespuesta.objects.create(
                    sesion=sesion,
                    usuario=request.user,
                    imagen=imagen,
                    respuesta=respuesta,
                    es_correcta=es_correcta,
                )

                respuesta_usuario_label = "IA" if respuesta == "IA" else "SINTÉTICA"
                respuesta_correcta_label = "IA" if imagen.tipo_origen == "IA" else "SINTÉTICA"

                request.session["feedback_data"] = {
                    "imagen_id": imagen.id,
                    "respuesta_usuario": respuesta_usuario_label,
                    "respuesta_correcta": respuesta_correcta_label,
                    "es_correcta": es_correcta,
                    "numero_actual": prueba_index + 1,
                    "total": len(prueba_ids),
                }

                request.session["prueba_index"] = prueba_index + 1
                return redirect("iniciar_prueba")

        elif accion == "finalizar":
            destinatario = request.POST.get("destinatario")

            if destinatario in ["DR_JORGE", "LUCIANO"]:
                sesion.destinatario = destinatario
                sesion.finalizada = True
                sesion.fecha_fin = timezone.now()
                sesion.save()

                total = sesion.respuestas.count()
                correctas = sesion.respuestas.filter(es_correcta=True).count()
                incorrectas = total - correctas

                request.session.flush()

                return render(request, "inicio/iniciar_prueba.html", {
                    "prueba_terminada": True,
                    "total": total,
                    "correctas": correctas,
                    "incorrectas": incorrectas,
                    "destinatario": destinatario,
                })

    feedback_data = request.session.pop("feedback_data", None)
    if feedback_data:
        imagen = get_object_or_404(ImagenValidacion, id=feedback_data["imagen_id"])
        return render(request, "inicio/iniciar_prueba.html", {
            "mostrar_feedback": True,
            "imagen": imagen,
            "respuesta_usuario": feedback_data["respuesta_usuario"],
            "respuesta_correcta": feedback_data["respuesta_correcta"],
            "es_correcta": feedback_data["es_correcta"],
            "numero_actual": feedback_data["numero_actual"],
            "total": feedback_data["total"],
        })

    if prueba_index >= len(prueba_ids):
        total = sesion.respuestas.count()
        correctas = sesion.respuestas.filter(es_correcta=True).count()
        incorrectas = total - correctas

        return render(request, "inicio/iniciar_prueba.html", {
            "seleccionar_destinatario": True,
            "total": total,
            "correctas": correctas,
            "incorrectas": incorrectas,
        })

    imagen_actual = get_object_or_404(ImagenValidacion, id=prueba_ids[prueba_index])

    return render(request, "inicio/iniciar_prueba.html", {
        "imagen": imagen_actual,
        "numero_actual": prueba_index + 1,
        "total": len(prueba_ids),
    })


# =========================
# PRUEBA PÚBLICA
# =========================

def iniciar_prueba_publica(request):
    if request.user.is_authenticated:
        return redirect("iniciar_prueba")

    if "prueba_publica_ids" not in request.session:
        imagenes_ids = list(
            ImagenValidacion.objects.filter(activa=True).values_list("id", flat=True)
        )

        if not imagenes_ids:
            return render(request, "inicio/iniciar_prueba_publica.html", {
                "sin_imagenes": True
            })

        random.shuffle(imagenes_ids)
        prueba_ids = imagenes_ids[:10]

        sesion = SesionPruebaPublica.objects.create()

        request.session["prueba_publica_ids"] = prueba_ids
        request.session["prueba_publica_index"] = 0
        request.session["sesion_prueba_publica_id"] = sesion.id

    prueba_ids = request.session.get("prueba_publica_ids", [])
    prueba_index = request.session.get("prueba_publica_index", 0)
    sesion_id = request.session.get("sesion_prueba_publica_id")

    if not sesion_id:
        return redirect("iniciar_prueba_publica")

    sesion = get_object_or_404(SesionPruebaPublica, id=sesion_id)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "responder":
            imagen_id = request.POST.get("imagen_id")
            respuesta = request.POST.get("respuesta")

            if imagen_id and respuesta:
                imagen = get_object_or_404(ImagenValidacion, id=imagen_id)
                es_correcta = imagen.tipo_origen == respuesta

                PruebaImagenRespuestaPublica.objects.create(
                    sesion=sesion,
                    imagen=imagen,
                    respuesta=respuesta,
                    es_correcta=es_correcta,
                )

                request.session["prueba_publica_index"] = prueba_index + 1
                return redirect("iniciar_prueba_publica")

    if prueba_index >= len(prueba_ids):
        return render(request, "inicio/iniciar_prueba_publica.html", {
            "seleccionar_destinatario": True,
            "form_participante": ParticipantePublicoForm(),
        })

    imagen_actual = get_object_or_404(ImagenValidacion, id=prueba_ids[prueba_index])

    return render(request, "inicio/iniciar_prueba_publica.html", {
        "imagen": imagen_actual,
        "numero_actual": prueba_index + 1,
        "total": len(prueba_ids),
    })


# =========================
# REGISTRO
# =========================

def register(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home2")
    else:
        form = RegistroForm()

    return render(request, "registration/register.html", {"form": form})


# =========================
# GRÁFICAS
# =========================

@staff_member_required
def admin_graficas(request):
    sexo = request.GET.get("sexo")

    respuestas_qs = PruebaImagenRespuesta.objects.select_related("usuario", "usuario__perfil")

    if sexo in ["H", "M", "P"]:
        respuestas_qs = respuestas_qs.filter(usuario__perfil__sexo=sexo)

    correctas = respuestas_qs.filter(es_correcta=True).count()
    incorrectas = respuestas_qs.filter(es_correcta=False).count()

    context = {
        "correctas": correctas,
        "incorrectas": incorrectas,
        "sexo": sexo or "",
    }

    return render(request, "admin/graficas.html", context)


@staff_member_required
def admin_graficas_publicas(request):
    sexo = request.GET.get("sexo")

    respuestas_qs = PruebaImagenRespuestaPublica.objects.all()

    if sexo in ["H", "M", "P"]:
        respuestas_qs = respuestas_qs.filter(participante__sexo=sexo)

    correctas = respuestas_qs.filter(es_correcta=True).count()
    incorrectas = respuestas_qs.filter(es_correcta=False).count()

    context = {
        "correctas": correctas,
        "incorrectas": incorrectas,
        "sexo": sexo or "",
    }

    return render(request, "admin/graficas_publicas.html", context)


def graficas_publicas(request):
    respuestas_qs = PruebaImagenRespuestaPublica.objects.all()

    return render(request, "inicio/graficas_publicas.html", {
        "correctas": respuestas_qs.filter(es_correcta=True).count(),
        "incorrectas": respuestas_qs.filter(es_correcta=False).count(),
    })
