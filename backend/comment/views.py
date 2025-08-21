from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404

from comment.models import Comment
from comment.serializers import CommentSerializer

from task.models import Task

from project.models import ProjectUser


class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id).select_related('author', 'task')

    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs['task_id'])
        if not ProjectUser.objects.filter(project=task.project, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        serializer.save(author=self.request.user, task=task)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.select_related('author', 'task')

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.author != self.request.user and not ProjectUser.objects.filter(project=comment.task.project, user=self.request.user, role='admin').exists():
            raise PermissionDenied("Only the author or project admin can edit this comment.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not ProjectUser.objects.filter(project=instance.task.project, user=self.request.user, role='admin').exists():
            raise PermissionDenied("Only the author or project admin can delete this comment.")
        instance.delete()
