from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            if self.required:
                raise forms.ValidationError("Debes seleccionar al menos una imagen.")
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []
        single_file_clean = super().clean

        for file in data:
            cleaned_files.append(single_file_clean(file, initial))

        return cleaned_files


class MultipleImageUploadForm(forms.Form):
    imagenes = MultipleFileField(
        label="Seleccionar imágenes",
        required=True,
    )

    tipo_origen = forms.ChoiceField(
        choices=[
            ('IA', 'Imagen generada por IA'),
            ('NO_IA', 'Imagen no generada por IA'),
        ],
        label="Tipo de imagen"
    )

    seleccionada = forms.BooleanField(
        required=False,
        initial=True,
        label="Guardar también en base64"
    )

    activa = forms.BooleanField(
        required=False,
        initial=True,
        label="Activa"
    )