# Generated manually for CloudinaryField migration

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("validacion", "0004_sesionpruebapublica_pruebaimagenrespuestapublica_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagenvalidacion",
            name="imagen",
            field=cloudinary.models.CloudinaryField(
                "imagen",
                max_length=255,
            ),
        ),
    ]
