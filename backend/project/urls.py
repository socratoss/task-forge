from django.urls import path
from .views import (
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateDestroyAPIView,
    ProjectUserListCreateAPIView,
    ProjectUserRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    path('', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project-retrieve-update-destroy'),
    path('<int:project_id>/users/', ProjectUserListCreateAPIView.as_view(), name='project-user-list'),
    path('<int:project_id>/users/<int:user_id>/', ProjectUserRetrieveUpdateDestroyAPIView.as_view(), name='project-user-detail'),
]