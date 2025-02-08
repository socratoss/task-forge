from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectInvite, ProjectLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField(read_only=True)
    users = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'industry', 'admin', 'users', 'created_at', 'updated_at', 'description']
        read_only_fields = ['id', 'key', 'created_at', 'updated_at', 'admin']

    def create(self, validated_data):
        request_user = self.context['request'].user
        users = validated_data.pop('users', [])

        validated_data.pop('admin', None)
        project = Project.objects.create(admin=request_user, **validated_data)
        project.users.add(request_user)
        project.users.add(*users)

        return project

    def update(self, instance, validated_data):
        user = self.context.get('request').user if 'request' in self.context else None
        changes = {}

        for attr, value in validated_data.items():
            old_value = getattr(instance, attr, None)
            if old_value != value:
                changes[attr] = (old_value, value)

        instance = super().update(instance, validated_data)

        if user and changes:
            for attr, (old_val, new_val) in changes.items():
                ProjectLog.objects.create(
                    project=instance, user=user,
                    action=f"Changed {attr} from '{old_val}' to '{new_val}'"
                )

        return instance


class ProjectInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvite
        fields = ['id', 'project', 'email', 'invited_by', 'created_at', 'accepted']
        read_only_fields = ['id', 'invited_by', 'created_at', 'accepted']
