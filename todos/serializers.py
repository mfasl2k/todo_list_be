from rest_framework import serializers
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