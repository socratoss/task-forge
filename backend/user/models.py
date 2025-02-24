from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    job_title = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='media/', blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)

    objects = UserManager()


    def __str__(self):
        return self.email
