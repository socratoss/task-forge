from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from task.models import Task, Project
from project.models import ProjectUser
from django.utils import timezone


class TaskTests(TestCase):
    fixtures = ["task/fixtures/users.json", "task/fixtures/projects.json", "task/fixtures/tasks.json"]

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.get(email="admin@example.com")
        self.member_user = get_user_model().objects.get(email="member@example.com")
        self.non_member_user = get_user_model().objects.get(email="nonmember@example.com")
        self.project = Project.objects.get(id=1)
        self.task = Task.objects.get(id=1)

    def authenticate_user(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    def test_list_tasks_as_member(self):
        self.authenticate_user(self.member_user)
        url = reverse("task-list-create", kwargs={"project_id": self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(task['project_id'] == self.project.id for task in response.data))

    def test_create_task_as_member(self):
        self.authenticate_user(self.member_user)
        url = reverse("task-list-create", kwargs={"project_id": self.project.id})
        project_user = ProjectUser.objects.get(project=self.project, user=self.member_user)
        data = {
            "name": "New Task",
            "description": "Task description",
            "status": "to_do",
            "priority": "medium",
            "task_type": "task",
            "assignee": project_user.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Task created successfully.")
        self.assertEqual(response.data['task']['name'], "New Task")

    def test_update_task_as_reporter(self):
        self.authenticate_user(self.task.reporter)
        url = reverse("task-detail", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        data = {"name": "Updated Task Name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Task updated successfully.")
        self.assertEqual(response.data['task']['name'], "Updated Task Name")

    def test_delete_task_as_admin(self):
        self.authenticate_user(self.project.admin)
        url = reverse("task-detail", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Task deleted successfully.")
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

    def test_task_board_get(self):
        self.authenticate_user(self.member_user)
        url = reverse("task-board", kwargs={"project_id": self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("to_do", response.data)
        self.assertIn("in_progress", response.data)
        self.assertIn("core_review", response.data)
        self.assertIn("done", response.data)

    def test_task_board_move_task(self):
        self.authenticate_user(self.member_user)
        url = reverse("task-board", kwargs={"project_id": self.project.id})
        data = {
            "task_id": self.task.id,
            "new_status": "in_progress",
            "new_order": 0
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Task moved successfully.")
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "in_progress")
        self.assertEqual(self.task.order, 0)

    def test_unauthorized_access(self):
        self.client.credentials()  # Remove authentication
        url = reverse("task-list-create", kwargs={"project_id": self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_denied_not_member(self):
        self.authenticate_user(self.non_member_user)
        url = reverse("task-list-create", kwargs={"project_id": self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_permission_denied(self):
        self.authenticate_user(self.non_member_user)
        url = reverse("task-detail", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        data = {"name": "Unauthorized Update"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_invalid_assignee(self):
        self.authenticate_user(self.member_user)
        url = reverse("task-list-create", kwargs={"project_id": self.project.id})
        other_project_user = ProjectUser.objects.get(project=2, user=self.non_member_user)
        data = {
            "name": "Invalid Assignee Task",
            "assignee": other_project_user.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee", response.data)

    def test_update_task_past_due_date(self):
        self.authenticate_user(self.task.reporter)
        url = reverse("task-detail", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        past_date = (timezone.now() - timezone.timedelta(days=1)).isoformat()
        data = {"due_date": past_date}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)
