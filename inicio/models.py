from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    SEXO_OPCIONES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('P', 'Prefiero mantenerlo privado'),
    ]

    ROL_OPCIONES = [
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('investigador', 'Investigador'),
        ('administrativo', 'Administrativo'),
        ('otro', 'Otro'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    edad = models.PositiveIntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES)
    rol = models.CharField(max_length=20, choices=ROL_OPCIONES)

    def __str__(self):
        return self.usuario.username


class ParticipantePublico(models.Model):
    SEXO_OPCIONES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('P', 'Prefiero mantenerlo privado'),
    ]

    NIVEL_ESTUDIO_OPCIONES = [
        ('secundaria', 'Secundaria'),
        ('tecnico', 'Técnico'),
        ('universitario', 'Universitario'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    edad = models.PositiveIntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES)
    nivel_estudio = models.CharField(max_length=20, choices=NIVEL_ESTUDIO_OPCIONES)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre