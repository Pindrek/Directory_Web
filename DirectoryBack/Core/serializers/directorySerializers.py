from rest_framework import serializers
from Core.models import Directory

class DirectoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = ['directory_name']

class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = '__all__'