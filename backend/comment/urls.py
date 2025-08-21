from django.urls import path
from comment.views import CommentListCreateView, CommentDetailView


urlpatterns = [
    path('', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
]
