from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth import authenticate

from .serializers import TaskSerializer, UserRegistrationSerializer, UserLoginSerializer
from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all tasks
        for the currently authenticated user.
        """
        return Task.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def perform_create(self, serializer):
        """
        Create a new task for the current user
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Update an existing task
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()

        # Get the new status from request data
        new_status = request.data.get('status')

        # Validate the status value
        valid_statuses = [status[0] for status in Task.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Choose from {valid_statuses}'}
            )

        # Update the status
        task.status = new_status

        # Auto-update completed field if status is 'completed'
        if new_status == 'completed':
            task.completed = True
        elif new_status == 'pending' or new_status == 'in_progress':
            task.completed = False

        task.save()

        # Return the updated task
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a task
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response({'message': 'Task deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user registration
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Create the user
            user = serializer.save()

            # Prepare response data
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'token': Token.objects.get(user=user).key
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user login
        """
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            # Authenticate user
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )

            if user:
                # Get or create token for the user
                token, _ = Token.objects.get_or_create(user=user)

                # Prepare response data
                response_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'token': token.key
                }

                return Response(response_data, status=status.HTTP_200_OK)

            # Authentication failed
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    """

    def post(self, request):
        """
        Handle user logout by deleting the user's token
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Unable to logout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentUserView(APIView):
    """
    API endpoint to retrieve current user information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle retrieving current user details
        """
        user = request.user

        # Prepare response data
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                # Add any additional user fields you want to expose
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)