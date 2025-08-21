from rest_framework import permissions

from project.models import Project, ProjectUser

from django.core.exceptions import ObjectDoesNotExist


class IsProjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "project"):
            return obj.project.admin == request.user
        return obj.admin == request.user

    def has_permission(self, request, view):
        if request.method == "POST":
            project_id = view.kwargs.get("project_id")
            try:
                project = Project.objects.get(id=project_id)
                return project.admin == request.user
            except ObjectDoesNotExist:
                return False
        return True


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
