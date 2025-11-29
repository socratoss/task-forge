from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user.models import User
from project.models import Project, ProjectUser


class ProjectTests(APITestCase):
    fixtures = ["project/tests/users.json", "project/tests/projects.json"]

    def setUp(self):
        self.admin_user = User.objects.get(pk=1)
        self.member_user = User.objects.get(pk=2)
        self.project = Project.objects.get(pk=1)

        self.project_list_url = reverse("project-list-create")
        self.project_detail_url = reverse("project-retrieve-update-destroy", kwargs={"project_id": self.project.id})
        self.project_users_list_url = reverse("project-user-list", kwargs={"project_id": self.project.id})
        self.project_user_detail_url = reverse("project-user-detail", kwargs={"project_id": self.project.id, "user_id": self.member_user.id})

    def test_create_project_authenticated(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.project_list_url, {
            "name": "New Project",
            "industry": "IT",
            "description": "A new project"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Project")
        self.assertEqual(response.data["admin"], self.admin_user.id)
        self.assertTrue(ProjectUser.objects.filter(project__name="New Project", user=self.admin_user, role="member").exists())

    def test_create_project_unauthenticated(self):
        response = self.client.post(self.project_list_url, {
            "name": "New Project",
            "industry": "IT"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_projects_authenticated(self):
        self.client.force_login(self.member_user)
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Project")

    def test_list_projects_unauthenticated(self):
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_project_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Project")
        self.assertEqual(response.data["admin"], self.admin_user.id)

    def test_retrieve_project_member(self):
        self.client.force_login(self.member_user)
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Project")

    def test_retrieve_project_unauthenticated(self):
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.patch(self.project_detail_url, {"name": "Updated Project"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

    def test_update_project_member(self):
        self.client.force_login(self.member_user)
        response = self.client.patch(self.project_detail_url, {"name": "Updated Project"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.delete(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_member(self):
        self.client.force_login(self.member_user)
        response = self.client.delete(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_project_user_admin(self):
        self.client.force_login(self.admin_user)
        new_user = User.objects.create_user(email="newuser@gmail.com", password="password")
        response = self.client.post(self.project_users_list_url, {
            "user": new_user.id,
            "role": "member"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProjectUser.objects.filter(project=self.project, user=new_user, role="member").exists())

    def test_add_project_user_member(self):
        self.client.force_login(self.member_user)
        new_user = User.objects.create_user(email="newuser@gmail.com", password="password")
        response = self.client.post(self.project_users_list_url, {
            "user": new_user.id,
            "role": "member"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_project_users_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.project_users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_project_users_member(self):
        self.client.force_login(self.member_user)
        response = self.client.get(self.project_users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        user_ids = [item["user"]["id"] for item in response.data]
        self.assertIn(self.admin_user.id, user_ids)
        self.assertIn(self.member_user.id, user_ids)

    def test_update_project_user_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.patch(self.project_user_detail_url, {"role": "member"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_user = ProjectUser.objects.get(project=self.project, user=self.member_user)
        self.assertEqual(project_user.role, "member")

    def test_update_project_user_member(self):
        self.client.force_login(self.member_user)
        response = self.client.patch(self.project_user_detail_url, {"role": "member"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_user_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.delete(self.project_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProjectUser.objects.filter(project=self.project, user=self.member_user).exists())

    def test_delete_project_user_member(self):
        self.client.force_login(self.member_user)
        response = self.client.delete(self.project_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_admin_from_project_users(self):
        self.client.force_login(self.admin_user)
        admin_detail_url = reverse("project-user-detail", kwargs={"project_id": self.project.id, "user_id": self.admin_user.id})
        response = self.client.delete(admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "The owner cannot remove themselves")
