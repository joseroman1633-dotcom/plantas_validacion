from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, ParticipantePublico


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    edad = forms.IntegerField(min_value=1, max_value=120)

    sexo = forms.ChoiceField(
        choices=PerfilUsuario.SEXO_OPCIONES
    )

    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROL_OPCIONES
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "edad",
            "sexo",
            "rol",
            "password1",
            "password2"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "auth__input"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            PerfilUsuario.objects.create(
                usuario=user,
                edad=self.cleaned_data["edad"],
                sexo=self.cleaned_data["sexo"],
                rol=self.cleaned_data["rol"]
            )

        return user


class ParticipantePublicoForm(forms.ModelForm):
    class Meta:
        model = ParticipantePublico
        fields = [
            "nombre",
            "correo",
            "edad",
            "sexo",
            "nivel_estudio",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "auth__input"})