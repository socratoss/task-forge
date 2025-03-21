from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Project, ProjectUser
from .serializers import ProjectSerializer, ProjectUserSerializer, ProjectUserCreateSerializer, ProjectUserUpdateSerializer
from .choices import RoleChoices


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            Q(admin=self.request.user) | Q(project_users__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            Q(admin=self.request.user) | Q(project_users__user=self.request.user)
        ).distinct()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'admin' in request.data and request.data['admin'] != str(instance.admin.id):
            return Response({'error': 'You cannot change the owner of a project through this request.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.admin != request.user:
            return Response({'error': 'Only the owner of the project can delete it.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ProjectUserListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectUser.objects.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectUserCreateSerializer
        return ProjectUserSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        if project.admin != self.request.user:
            raise permissions.PermissionDenied("Only the project owner can add members.")
        serializer.save(project=project)


class ProjectUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectUser.objects.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectUserUpdateSerializer
        return ProjectUserSerializer

    def update(self, request, *args, **kwargs):
        project = self.get_object().project
        if project.admin != request.user:
            return Response({'error': 'Only the project owner can change roles.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project_user = self.get_object()
        project = project_user.project
        if project.admin != request.user:
            return Response({'error': 'Only the project owner can remove members'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)