import uuid
from django.db import models
from django.conf import settings as django_settings


class Project(models.Model):
    INDUSTRY_CHOICES = [
        ('IT', 'IT'),
        ('Marketing', 'Marketing'),
        ('Education', 'Education'),
        ('Healthcare', 'Healthcare'),
        ('Finance', 'Finance'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=8, unique=True, blank=True)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='Other')
    admin = models.ForeignKey(
        django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_projects'
    )
    users = models.ManyToManyField(
        django_settings.AUTH_USER_MODEL, through='ProjectUser', related_name='projects', blank=True
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_unique_key(self):
        while True:
            key = uuid.uuid4().hex[:8]
            if not Project.objects.filter(key=key).exists():
                return key

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.key:
            self.key = self.generate_unique_key()
        super().save(*args, **kwargs)

        if is_new:
            ProjectLog.objects.create(project=self, user=self.admin, action="Created project")
        else:
            old_project = Project.objects.filter(pk=self.pk).first()
            if old_project and old_project.name != self.name:
                ProjectLog.objects.create(
                    project=self, user=self.admin,
                    action=f"Changed project name from '{old_project.name}' to '{self.name}'"
                )

    def __str__(self):
        return self.name


class ProjectUser(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_users')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    class Meta:
        db_table = "project_project_users"
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='unique_user_project')
        ]

    def __str__(self):
        return f"{self.user} - {self.project} ({self.role})"


class ProjectLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} - {self.action}"


class ProjectInvite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    invited_by = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite to {self.project.name} - {self.email}"
