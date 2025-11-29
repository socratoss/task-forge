from rest_framework import serializers

from project.models import Project, ProjectUser

from user.models import User
from user.serializers import UserSerializer

from project.choices import RoleChoices


class ProjectUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectUser
        fields = ["user", "role"]


class ProjectSerializer(serializers.ModelSerializer):
    users = ProjectUserSerializer(source="project_users", many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "key", "industry", "admin", "users", "description", "created_at", "updated_at"]
        read_only_fields = ["key", "admin"]


class ProjectUserCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(choices=RoleChoices.choices)

    class Meta:
        model = ProjectUser
        fields = ["user", "role"]


class ProjectUserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleChoices.choices)

    class Meta:
        model = ProjectUser
        fields = ["role"]
