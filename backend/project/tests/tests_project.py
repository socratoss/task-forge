from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from project.models import Project
from django.contrib.auth import get_user_model


class ProjectTests(APITestCase):
    fixtures = ['project/tests/fixtures.json']

    def setUp(self):
        self.admin_user = get_user_model().objects.get(pk=1)
        self.project_list_url = reverse('project-list')
        self.create_project_url = reverse('project-list')
        self.detail_project_url = lambda project_id: reverse('project-detail', kwargs={'pk': project_id})

    def test_create_project(self):
        self.client.force_login(self.admin_user)

        data = {
            "name": "new-test-project",
            "type": "High"
        }
        response = self.client.post(self.create_project_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(name="new-test-project").exists())
        self.assertIsNotNone(response.data["key"])

    def test_list_projects(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.project_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_project_detail(self):
        self.client.force_login(self.admin_user)

        project = Project.objects.get(name="quantum-roadmap")
        response = self.client.get(self.detail_project_url(project.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "quantum-roadmap")

    def test_project_key_autogeneration(self):
        self.client.force_login(self.admin_user)

        project = Project.objects.create(name="AI-roadmap", admin=self.admin_user)

        self.assertIsNotNone(project.key)
        self.assertTrue(len(project.key) > 0)

    def test_unique_project_keys(self):
        self.client.force_login(self.admin_user)

        project1 = Project.objects.create(name="Test-1", admin=self.admin_user)
        project2 = Project.objects.create(name="Test-2", admin=self.admin_user)

        self.assertNotEqual(project1.key, project2.key)

    def test_project_str(self):
        project = Project.objects.get(name="quantum-roadmap")
        self.assertEqual(str(project), "quantum-roadmap")
