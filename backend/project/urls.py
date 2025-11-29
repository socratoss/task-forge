from django.urls import path

from project.views import (
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateDestroyAPIView,
    ProjectUserListCreateAPIView,
    ProjectUserRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("<int:project_id>/", ProjectRetrieveUpdateDestroyAPIView.as_view(), name="project-retrieve-update-destroy"),
    path("<int:project_id>/users/", ProjectUserListCreateAPIView.as_view(), name="project-user-list"),
    path("<int:project_id>/users/<int:user_id>/", ProjectUserRetrieveUpdateDestroyAPIView.as_view(), name="project-user-detail"),
]
