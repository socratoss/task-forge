from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db import models

from project.models import Project, ProjectUser

from task.models import Task
from task.serializers import TaskSerializer
from task.permissions import IsProjectMemberOrOwner


class TaskListCreateView(generics.ListCreateAPIView):
    """
    API view to list tasks within a specific project or create a new task for that project.
    """
    permission_classes = [IsAuthenticated, IsProjectMemberOrOwner]
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "status", "order", "due_date", "created_at"]
    ordering = ["status", "order"]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        return Task.objects.filter(project=project).select_related("assignee", "reporter", "project")

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        if not ProjectUser.objects.filter(project=project, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        assignee = serializer.validated_data.get("assignee")
        if assignee and not ProjectUser.objects.filter(project=project, user=assignee).exists():
            raise ValidationError({"assignee": "The assigned user is not a member of this project."})
        serializer.save(reporter=self.request.user, project=project)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            {"message": "Task created successfully.", "task": response.data},
            status=status.HTTP_201_CREATED
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific task within a project.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_field = "id"
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        return Task.objects.filter(project=project).select_related("assignee", "reporter", "project")

    def perform_update(self, serializer):
        task = self.get_object()
        if self.request.user not in [task.project.admin, task.reporter, task.assignee]:
            raise PermissionDenied("You do not have permission to modify this task.")
        serializer.validated_data.pop("reporter", None)
        serializer.validated_data.pop("project", None)
        assignee = serializer.validated_data.get("assignee")
        if assignee and not ProjectUser.objects.filter(project=task.project, user=assignee).exists():
            raise ValidationError({"assignee": "The assigned user is not a member of this project."})
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user not in [instance.project.admin, instance.reporter, instance.assignee]:
            raise PermissionDenied("You do not have permission to delete this task.")
        with transaction.atomic():
            Task.objects.filter(
                project=instance.project,
                status=instance.status,
                order__gt=instance.order
            ).update(order=models.F("order") - 1)
            instance.delete()

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response(
            {"message": "Task updated successfully.", "task": response.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response(
            {"message": "Task updated successfully.", "task": response.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response(
            {"message": "Task deleted successfully."},
            status=status.HTTP_200_OK
        )


class TaskBoardView(APIView):
    """
    API view to retrieve the task board layout or move tasks between statuses/positions.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if not ProjectUser.objects.filter(project=project, user=request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        tasks = Task.objects.filter(project=project).order_by("status", "order").select_related("assignee", "reporter")
        serializer = TaskSerializer(tasks, many=True, context={"request": request})
        board_data = {status_key: [] for status_key, _ in Task.Status.choices}
        for task_data in serializer.data:
            board_data[task_data["status"]].append(task_data)
        return Response(board_data, status=status.HTTP_200_OK)

    def patch(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if not ProjectUser.objects.filter(project=project, user=request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        task_id = request.data.get("task_id")
        new_status = request.data.get("new_status")
        new_order = request.data.get("new_order")
        if not all([task_id, new_status, new_order is not None]):
            return Response(
                {"error": "task_id, new_status, and new_order are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        task = get_object_or_404(Task, id=task_id, project=project)
        if request.user not in [task.project.admin, task.reporter, task.assignee]:
            raise PermissionDenied("You do not have permission to modify this task.")
        if new_status not in Task.Status.values:
            return Response(
                {"error": f"Invalid status. Valid statuses are: {Task.Status.values}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            new_order = int(new_order)
            if new_order < 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "new_order must be a non-negative integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            task.move_to_position(new_status=new_status, new_order=new_order)
        serializer = TaskSerializer(task, context={"request": request})
        return Response(
            {"message": "Task moved successfully.", "task": serializer.data},
            status=status.HTTP_200_OK
        )
