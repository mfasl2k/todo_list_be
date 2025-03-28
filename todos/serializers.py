from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create a new task for the current user
        """
        validated_data.pop('user', None)
        user = self.context['request'].user
        return Task.objects.create(user=user, **validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        """
        Validate that the two passwords match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create a new user and generate an authentication token
        """
        # Remove password2 from validated data
        validated_data.pop('password2')

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Generate token for the user
        Token.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )