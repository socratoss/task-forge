from rest_framework import permissions
from project.models import Project, ProjectUser
from django.core.exceptions import ObjectDoesNotExist


class IsProjectMemberOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")
        try:
            project = Project.objects.get(id=project_id)
            return project.admin == request.user or ProjectUser.objects.filter(
                project=project, user=request.user
            ).exists()
        except ObjectDoesNotExist:
            return False
