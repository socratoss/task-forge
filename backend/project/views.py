from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from project.models import Project, ProjectUser
from project.serializers import ProjectSerializer
from project.choices import RoleChoices


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Project.objects.filter(users=self.request.user) |
            Project.objects.filter(admin=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """Создает проект и автоматически добавляет пользователя как владельца"""
        project = serializer.save(admin=self.request.user)
        ProjectUser.objects.create(user=self.request.user, project=project, role=RoleChoices.OWNER)


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Project.objects.filter(users=self.request.user) |
            Project.objects.filter(admin=self.request.user)
        ).distinct()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.admin != request.user:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
