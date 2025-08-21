from django.urls import path

from task.views import (
    TaskListCreateView,
    TaskDetailView,
    TaskBoardView,
)


urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path("board/", TaskBoardView.as_view(), name="task-board"),
]
