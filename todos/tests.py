# todos/tests.py
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import Task


class TaskAPITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Create a token for the test user
        self.token = Token.objects.create(user=self.user)

        # Create test tasks
        self.task1 = Task.objects.create(
            user=self.user,
            title='Test Task 1',
            description='Description for test task 1',
            priority='high'
        )

        self.task2 = Task.objects.create(
            user=self.user,
            title='Test Task 2',
            description='Description for test task 2',
            priority='medium'
        )

        # Set up the API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # URLs
        self.list_create_url = reverse('task-list')

    def test_get_task_list(self):
        """Test retrieving a list of tasks"""
        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Test Task 1')
        self.assertEqual(response.data[1]['title'], 'Test Task 2')

    def test_get_task_list_unauthorized(self):
        """Test accessing tasks without authentication fails"""
        # Remove authentication credentials
        self.client.credentials()

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task(self):
        """Test creating a new task"""
        new_task_data = {
            'title': 'New Test Task',
            'description': 'This is a new test task',
            'priority': 'low'
        }

        response = self.client.post(self.list_create_url, new_task_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(response.data['title'], new_task_data['title'])
        self.assertEqual(response.data['description'], new_task_data['description'])
        self.assertEqual(response.data['priority'], new_task_data['priority'])

        # Verify the task is associated with the user
        created_task = Task.objects.get(title='New Test Task')
        self.assertEqual(created_task.user, self.user)

    def test_create_task_unauthorized(self):
        """Test creating a task without authentication fails"""
        # Remove authentication credentials
        self.client.credentials()

        new_task_data = {
            'title': 'Unauthorized Task',
            'description': 'This should not be created',
        }

        response = self.client.post(self.list_create_url, new_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Task.objects.count(), 2)  # No new task should be created

    def test_create_task_missing_title(self):
        """Test that creating a task without a title fails validation"""
        invalid_task_data = {
            'description': 'This task has no title',
            'priority': 'medium'
        }

        response = self.client.post(self.list_create_url, invalid_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)  # Should contain an error for title

    def test_create_task_with_different_user(self):
        """Test that tasks created by different users are isolated"""
        # Create a second user and authenticate as them
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword123'
        )

        token2 = Token.objects.create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')

        # Create a task as user2
        new_task_data = {
            'title': 'User2 Task',
            'description': 'This task belongs to user2',
        }

        response = self.client.post(self.list_create_url, new_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get tasks for user2 - should only see their own task
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'User2 Task')

        # Switch back to user1 and verify they only see their tasks
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [task['title'] for task in response.data]
        self.assertIn('Test Task 1', titles)
        self.assertIn('Test Task 2', titles)
        self.assertNotIn('User2 Task', titles)


# To run these tests:
# python manage.py test todos
from django.test import TestCase

# Create your tests here.
