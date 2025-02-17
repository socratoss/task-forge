from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import Project, ProjectUser
from .serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(users=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(admin=self.request.user)
        ProjectUser.objects.create(user=self.request.user, project=project, role='owner')


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(users=self.request.user)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.admin != request.user:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
