from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectListCreateView,
    ProjectRetrieveUpdateDestroyView,
)


router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('create/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('detail/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project-detail'),
]