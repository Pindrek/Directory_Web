from rest_framework import serializers
from Core.models import File

class FileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'img',
            'file_name',
            'directory',
        ]

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'