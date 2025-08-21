from django.db import models, transaction
from django.conf import settings
from django.utils import timezone

from project.models import Project


class Task(models.Model):
    class Status(models.TextChoices):
        TO_DO = "to_do", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        CORE_REVIEW = "core_review", "Core Review"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class TaskType(models.TextChoices):
        TASK = "task", "Task"
        BUG = "bug", "Bug"
        STORY = "story", "Story"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_tasks"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TO_DO)
    order = models.PositiveIntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    task_type = models.CharField(max_length=10, choices=TaskType.choices, default=TaskType.TASK)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["project", "status", "order"]
        indexes = [
            models.Index(fields=["project", "status", "order"]),
            models.Index(fields=["assignee"]),
            models.Index(fields=["reporter"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["task_type"])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "status", "order"],
                name="unique_task_order_per_project_status"
            )
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.order == 0:
            max_order = Task.objects.filter(project=self.project, status=self.status).aggregate(
                models.Max("order")
            )["order__max"] or 0
            self.order = max_order + 1
        super().save(*args, **kwargs)

    def move_to_position(self, new_status, new_order):
        old_status = self.status
        old_order = self.order
        new_order = max(0, int(new_order))
        with transaction.atomic():
            if old_status == new_status:
                if new_order < old_order:
                    Task.objects.filter(
                        project=self.project,
                        status=old_status,
                        order__gte=new_order,
                        order__lt=old_order
                    ).update(order=models.F("order") + 1)
                elif new_order > old_order:
                    Task.objects.filter(
                        project=self.project,
                        status=old_status,
                        order__gt=old_order,
                        order__lte=new_order
                    ).update(order=models.F("order") - 1)
            else:
                Task.objects.filter(
                    project=self.project,
                    status=old_status,
                    order__gt=old_order
                ).update(order=models.F("order") - 1)
                Task.objects.filter(
                    project=self.project,
                    status=new_status,
                    order__gte=new_order
                ).update(order=models.F("order") + 1)
            self.status = new_status
            self.order = new_order
            self.updated_at = timezone.now()
            self.save(update_fields=["status", "order", "updated_at"])

    def __str__(self):
        return f"{self.project.key}-{self.id}: {self.name}"
