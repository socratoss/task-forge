from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectListCreateView,
    ProjectRetrieveUpdateDestroyView,
    AcceptInviteView,
    ProjectInviteView,
    AcceptInviteRedirectView
)


router = DefaultRouter()


urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project-detail'),
    path('projects/<int:pk>/invite/', ProjectInviteView.as_view(), name='send-invite'),
    path('projects/invites/<int:pk>/accept/', AcceptInviteView.as_view(), name='accept-invite'),
    path('projects/invites/<int:pk>/', AcceptInviteRedirectView.as_view(), name='invite-redirect'),
    path('', include(router.urls)),
] 