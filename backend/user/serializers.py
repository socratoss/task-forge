from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'job_title', 'profile_picture']


class LoginSerializer(BaseLoginSerializer):
    email = None