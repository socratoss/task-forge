from rest_framework import serializers
from user.models import User
from .models import Project, ProjectUser
from .choices import RoleChoices


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'industry', 'admin', 'description', 'created_at', 'updated_at']
        read_only_fields = ['key']


class ProjectUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectUser
        fields = ['user', 'role']


class ProjectUserCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(choices=RoleChoices.choices)

    class Meta:
        model = ProjectUser
        fields = ['user', 'role']


class ProjectUserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleChoices.choices)

    class Meta:
        model = ProjectUser
        fields = ['role']