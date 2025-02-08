from django.urls import reverse
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from rest_framework.views import APIView

from .models import Project, ProjectInvite, ProjectLog, ProjectUser
from .serializers import ProjectSerializer, ProjectInviteSerializer


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


class ProjectInviteView(generics.CreateAPIView):
    serializer_class = ProjectInviteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        project_id = kwargs.get('pk')
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.get(id=project_id)
        if request.user != project.admin:
            return Response({'error': 'Only the admin can invite users'},
                            status=status.HTTP_403_FORBIDDEN)

        if request.user.email == email:
            return Response({'error': 'You cannot invite yourself'}, status=status.HTTP_400_BAD_REQUEST)

        if project.users.filter(email=email).exists():
            return Response({'error': 'User is already a project member'}, status=status.HTTP_400_BAD_REQUEST)

        invite, created = ProjectInvite.objects.get_or_create(
            project=project, email=email, defaults={'invited_by': request.user}
        )

        invite_url = request.build_absolute_uri(
            reverse('accept-invite', kwargs={'pk': invite.id})
        )

        send_mail(
            subject="You're invited to join a project on TeamFix!",
            message=f"You have been invited to join the project on TeamFix.\n\n"
                    f"Click the link below to accept the invitation and start collaborating:\n"
                    f"{invite_url}\n\n"
                    f"If you did not request this invitation, you can safely ignore this email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Invitation sent!", "invite_url": invite_url})


class AcceptInviteRedirectView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        invite = get_object_or_404(ProjectInvite, id=pk)
        user_exists = User.objects.filter(email=invite.email).exists()
        next_url = reverse('accept-invite', kwargs={'pk': pk})
        return redirect(f"/api/authentication/{'login' if user_exists else 'signup'}/?next={next_url}")


class AcceptInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        invite = get_object_or_404(ProjectInvite, id=pk)
        if invite.email != request.user.email:
            return Response({'error': 'You cannot accept this invitation'}, status=status.HTTP_403_FORBIDDEN)

        project = invite.project
        project.users.add(request.user)
        invite.delete()

        ProjectLog.objects.create(project=project, user=request.user, action="Accepted project invite")

        return redirect(reverse('project-detail', kwargs={'pk': project.id}))