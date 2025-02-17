from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'industry', 'admin', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'key', 'created_at', 'updated_at']
