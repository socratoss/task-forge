from rest_framework import serializers
from django.utils import timezone
from task.models import Task
from project.models import Project, ProjectUser
from user.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee_details = UserSerializer(source="assignee", read_only=True)
    reporter = UserSerializer(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=ProjectUser.objects.all().select_related("user"),
        write_only=True,
        allow_null=True,
        required=False
    )
    project_id = serializers.IntegerField(read_only=True, source="project.id")
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    task_type_display = serializers.CharField(source="get_task_type_display", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "name", "description", "project_id", "assignee_details", "reporter",
            "assignee", "status", "status_display", "priority", "priority_display",
            "task_type", "task_type_display", "order", "due_date", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "project_id", "assignee_details", "reporter", "order",
            "created_at", "updated_at", "status_display", "priority_display", "task_type_display"
        ]

    def validate_assignee(self, value):
        project_id = self.context["view"].kwargs.get("project_id")
        project = Project.objects.get(id=project_id)
        if value and not ProjectUser.objects.filter(project=project, user=value.user).exists():
            raise serializers.ValidationError("The assigned user is not a member of this project.")
        return value.user if value else None

    def validate_due_date(self, value):
        if value and value.date() < timezone.now().date():
            raise serializers.ValidationError("The due date cannot be in the past.")
        return value
