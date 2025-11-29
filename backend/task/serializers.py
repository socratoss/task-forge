from rest_framework import serializers

from django.utils import timezone

from task.models import Task

from project.models import Project, ProjectUser

from user.models import User
from user.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee_details = UserSerializer(source="assignee", read_only=True)
    reporter = UserSerializer(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
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

    def validate(self, data):
        project_id = self.context["view"].kwargs.get("project_id")
        project = Project.objects.get(id=project_id)
        assignee = data.get("assignee")
        if assignee and not ProjectUser.objects.filter(project=project, user=assignee).exists():
            raise serializers.ValidationError({"assignee": "The assigned user is not a member of this project."})
        due_date = data.get("due_date")
        if due_date and due_date.date() < timezone.now().date():
            raise serializers.ValidationError({"due_date": "The due date cannot be in the past."})
        return data
