import base64
from rest_framework import serializers
from .models import ImagenValidacion


class ImagenValidacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenValidacion
        fields = '__all__'
        read_only_fields = ('subida_por', 'fecha_subida', 'imagen_base64')

    def create(self, validated_data):
        imagen_file = validated_data.get('imagen')
        seleccionada = validated_data.get('seleccionada', False)

        if imagen_file and seleccionada:
            imagen_file.seek(0)
            validated_data['imagen_base64'] = base64.b64encode(imagen_file.read()).decode('utf-8')
            imagen_file.seek(0)

        return super().create(validated_data)