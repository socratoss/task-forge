from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Project, ProjectLog, ProjectUser
from .serializers import ProjectSerializer


User = get_user_model()


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(users=self.request.user).select_related('admin').prefetch_related('users')

    def perform_create(self, serializer):
        project = serializer.save(admin=self.request.user)
        project.users.add(self.request.user)
        ProjectLog.objects.create(project=project, user=self.request.user, action="Created project")


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(users=self.request.user).select_related('admin').prefetch_related('users')

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        project = self.get_object()

        if project.admin != request.user:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        old_name = project.name
        response = super().update(request, *args, **kwargs)
        project.refresh_from_db()

        action_message = (f"Changed project name from '{old_name}' to '{project.name}'"
                          if old_name != project.name else "Updated project")
        ProjectLog.objects.create(project=project, user=request.user, action=action_message)

        return response

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()

        if project.admin != request.user:
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)

        ProjectLog.objects.create(project=project, user=request.user, action="Deleted project")
        return super().destroy(request, *args, **kwargs)


class ProjectUserManagementView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        project = self.get_object()
        user = User.objects.get(id=request.data.get("user_id"))
        ProjectUser.objects.get_or_create(user=user, project=project, role='member')
        ProjectLog.objects.create(project=project, user=request.user, action=f"Added {user.email} to project")
        return Response({"status": "User added"})

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        user = User.objects.filter(id=request.data.get("user_id")).first()
        if not user or not ProjectUser.objects.filter(user=user, project=project).exists():
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        ProjectUser.objects.filter(user=user, project=project).delete()
        ProjectLog.objects.create(project=project, user=request.user, action=f"Removed {user.email} from project")
        return Response({"status": "User removed"})

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        project = self.get_object()
        user = User.objects.filter(id=request.data.get("user_id")).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get("role")
        ProjectUser.objects.filter(user=user, project=project).update(role=new_role)
        ProjectLog.objects.create(project=project, user=request.user,
                                  action=f"Changed role of {user.email} to {new_role}")
        return Response({"status": "User role updated"})
