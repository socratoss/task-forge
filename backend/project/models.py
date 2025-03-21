import re
import random
import string
from django.db import models
from django.conf import settings as django_settings
from .choices import IndustryChoices, RoleChoices


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=8, unique=True, blank=True, editable=False)
    industry = models.CharField(max_length=20, choices=IndustryChoices.choices, default=IndustryChoices.OTHER)
    admin = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="admin_projects",
    )
    users = models.ManyToManyField(
        django_settings.AUTH_USER_MODEL,
        through="ProjectUser",
        related_name="projects",
        blank=True,
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _generate_base_key(self) -> str:
        words = re.findall(r"[A-Za-z]+", self.name)
        if len(words) > 1:
            return "".join(word[0].upper() for word in words)
        elif words:
            return words[0][:3].upper()
        return "X"

    def _generate_unique_key(self) -> str:
        base_key = self._generate_base_key()
        key = base_key


        cleaned_name = "".join(re.findall(r"[A-Za-z]+", self.name)).upper()
        reversed_letters = list(cleaned_name[::-1])

        idx = 0
        while Project.objects.filter(key=key).exists():
            if idx < len(reversed_letters):
                key = f"{base_key}{reversed_letters[idx]}"
                idx += 1
            else:
                key = f"{base_key}{random.choice(string.ascii_uppercase)}"
            if len(key) > 8:
                key = key[:8]

        return key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self._generate_unique_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProjectUser(models.Model):
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_users")
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.MEMBER, verbose_name="Role")

    class Meta:
        db_table = "project_project_users"
        constraints = [
            models.UniqueConstraint(fields=["user", "project"], name="unique_user_project")
        ]
        indexes = [
            models.Index(fields=["user", "project"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.project} ({self.role})"