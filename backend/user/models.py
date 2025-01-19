from django.contrib.auth.models import AbstractUser
from django.db import models
from user.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    job_title = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    objects = UserManager()

    def __str__(self):
        return self.email