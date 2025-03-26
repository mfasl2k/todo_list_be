from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import Task


class TaskAPITests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpassword123'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword456'
        )

        # Create tokens for test users
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        # Create test tasks for user1
        self.task1 = Task.objects.create(
            user=self.user1,
            title='Test Task 1',
            description='Description for test task 1',
            priority='high'
        )

        self.task2 = Task.objects.create(
            user=self.user1,
            title='Test Task 2',
            description='Description for test task 2',
            priority='medium'
        )

        # Set up API client for user1
        self.client1 = APIClient()
        self.client1.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')

        # Set up API client for user2
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')

        # URLs
        self.list_create_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.task1.pk})

    def test_create_task(self):
        """Test creating a new task"""
        new_task_data = {
            'title': 'New Test Task',
            'description': 'This is a new test task',
            'priority': 'low'
        }

        response = self.client1.post(self.list_create_url, new_task_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)

        # Verify the task is associated with the correct user
        created_task = Task.objects.get(title='New Test Task')
        self.assertEqual(created_task.user, self.user1)

    def test_delete_own_task(self):
        """Test deleting own task"""
        # Verify task exists before deletion
        self.assertTrue(Task.objects.filter(pk=self.task1.pk).exists())

        response = self.client1.delete(self.detail_url)

        # Check successful deletion
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the task is deleted
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=self.task1.pk)

        # Verify only one task remains for the user
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 1)

    def test_list_tasks(self):
        """Test retrieving list of tasks"""
        response = self.client1.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verify only user1's tasks are returned
        task_titles = [task['title'] for task in response.data]
        self.assertIn('Test Task 1', task_titles)
        self.assertIn('Test Task 2', task_titles)

    def test_update_own_task(self):
        """Test updating own task"""
        update_data = {
            'title': 'Updated Test Task',
            'description': 'Updated description'
        }

        response = self.client1.patch(self.detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh task and verify updates
        updated_task = Task.objects.get(pk=self.task1.pk)
        self.assertEqual(updated_task.title, 'Updated Test Task')
        self.assertEqual(updated_task.description, 'Updated description')

    def test_create_task_unauthenticated(self):
        """Test creating a task without authentication"""
        # Remove authentication
        client = APIClient()

        new_task_data = {
            'title': 'Unauthenticated Task',
            'description': 'Should not be created'
        }

        response = client.post(self.list_create_url, new_task_data, format='json')

        # Should be unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Task.objects.count(), 2)

    def test_list_tasks_unauthenticated(self):
        """Test listing tasks without authentication"""
        # Remove authentication
        client = APIClient()

        response = client.get(self.list_create_url)

        # Should be unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)