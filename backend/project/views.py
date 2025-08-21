from django.db.models import Q

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from project.models import Project, ProjectUser
from project.serializers import (
    ProjectSerializer, ProjectUserSerializer,
    ProjectUserCreateSerializer, ProjectUserUpdateSerializer
)
from project.choices import RoleChoices
from project.permissions import IsProjectOwner, IsProjectMemberOrOwner


class ProjectListCreateAPIView(ListCreateAPIView):
    """
    APIView for creating and getting a list of projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            Q(admin=self.request.user) | Q(project_users__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.save(admin=self.request.user)
        ProjectUser.objects.create(
            user=self.request.user,
            project=project,
            role=RoleChoices.MEMBER
        )


class ProjectRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    APIView for viewing, updating and deleting a project.
    """
    serializer_class = ProjectSerializer
    lookup_field = "id"
    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        return Project.objects.filter(
            Q(admin=self.request.user) | Q(project_users__user=self.request.user)
        ).distinct()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsProjectOwner()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop("admin", None)
        request._full_data = data
        return super().update(request, *args, **kwargs)


class ProjectUserListCreateAPIView(ListCreateAPIView):
    """
    APIView for listing and adding project members.
    """
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated(), IsProjectMemberOrOwner()]
        return [permissions.IsAuthenticated(), IsProjectOwner()]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return ProjectUser.objects.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectUserCreateSerializer
        return ProjectUserSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)


class ProjectUserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    APIView for viewing, updating and deleting a project member.
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
    lookup_field = "user__id"
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return ProjectUser.objects.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProjectUserUpdateSerializer
        return ProjectUserSerializer

    def destroy(self, request, *args, **kwargs):
        project_user = self.get_object()
        if project_user.user == project_user.project.admin:
            return Response({"error": "The owner cannot remove themselves"}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
