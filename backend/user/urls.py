from django.urls import path
from .views import UserDetailView


urlpatterns = [
    path('current/', UserDetailView.as_view(), name='user-profile'),
]
