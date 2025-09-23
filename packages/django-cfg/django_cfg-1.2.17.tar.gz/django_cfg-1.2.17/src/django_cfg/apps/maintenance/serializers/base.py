"""
Base serializers for maintenance app.

Common serializers used across the maintenance application.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = fields


class APIResponseSerializer(serializers.Serializer):
    """Generic API response serializer for OpenAPI documentation."""
    
    success = serializers.BooleanField(
        help_text="Whether the operation was successful"
    )
    message = serializers.CharField(
        required=False, 
        help_text="Response message"
    )
    data = serializers.JSONField(
        required=False, 
        help_text="Response data"
    )
    error = serializers.CharField(
        required=False, 
        help_text="Error message if failed"
    )
    errors = serializers.JSONField(
        required=False, 
        help_text="Detailed error information"
    )

