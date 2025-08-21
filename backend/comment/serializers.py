from rest_framework import serializers

from comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_username', 'text', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at', 'task']
