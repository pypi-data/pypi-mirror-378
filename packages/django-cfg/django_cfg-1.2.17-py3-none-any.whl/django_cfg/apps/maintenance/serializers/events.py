"""
Maintenance event serializers.

Serializers for MaintenanceEvent and MaintenanceLog models.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from ..models import MaintenanceEvent, MaintenanceLog, CloudflareSite
from .base import UserSerializer
from .sites import CloudflareSiteListSerializer


class MaintenanceLogSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceLog model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MaintenanceLog
        fields = [
            'id', 'event', 'level', 'message', 'component', 'operation',
            'user', 'metadata', 'timestamp'
        ]
        read_only_fields = fields
        extra_kwargs = {
            'level': {
                'help_text': 'Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
            },
            'message': {
                'help_text': 'Log message content'
            },
            'component': {
                'help_text': 'Component that generated the log (e.g., cloudflare, monitoring)'
            },
            'operation': {
                'help_text': 'Operation being performed (e.g., deploy_worker, health_check)'
            }
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Scheduled Maintenance',
            summary='A scheduled maintenance event',
            description='Example of a scheduled maintenance event for multiple sites',
            value={
                'title': 'Database Migration',
                'description': 'Upgrading database to PostgreSQL 14',
                'reason': 'scheduled',
                'estimated_duration': '02:00:00',
                'maintenance_message': 'We are performing scheduled maintenance. Please try again in 2 hours.',
                'sites': [1, 2, 3]
            }
        ),
        OpenApiExample(
            'Emergency Maintenance',
            summary='An emergency maintenance event',
            description='Example of an emergency maintenance event',
            value={
                'title': 'Security Patch',
                'description': 'Applying critical security updates',
                'reason': 'emergency',
                'estimated_duration': '00:30:00',
                'maintenance_message': 'Emergency maintenance in progress. Service will be restored shortly.',
                'sites': [1]
            }
        )
    ]
)
class MaintenanceEventSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceEvent model with full details."""
    
    initiated_by = UserSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    sites = CloudflareSiteListSerializer(many=True, read_only=True)
    logs = MaintenanceLogSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_scheduled = serializers.ReadOnlyField()
    affected_sites_count = serializers.ReadOnlyField()
    
    class Meta:
        model = MaintenanceEvent
        fields = [
            'id', 'title', 'description', 'reason', 'status', 'initiated_by',
            'completed_by', 'sites', 'logs', 'started_at', 'ended_at',
            'estimated_duration', 'maintenance_message', 'duration',
            'is_active', 'is_scheduled', 'affected_sites_count',
            'success_count', 'error_count_before', 'error_count_during',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'initiated_by', 'completed_by', 'sites', 'logs', 'duration',
            'is_active', 'is_scheduled', 'affected_sites_count', 'success_count',
            'error_count_before', 'error_count_during', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'title': {
                'help_text': 'Brief title describing the maintenance'
            },
            'description': {
                'help_text': 'Detailed description of the maintenance work'
            },
            'reason': {
                'help_text': 'Reason for maintenance (manual, scheduled, automatic, emergency)'
            },
            'maintenance_message': {
                'help_text': 'Message to display to users during maintenance'
            },
            'estimated_duration': {
                'help_text': 'Estimated duration in HH:MM:SS format'
            }
        }


class MaintenanceEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MaintenanceEvent."""
    
    sites = serializers.PrimaryKeyRelatedField(
        queryset=CloudflareSite.objects.all(),
        many=True,
        help_text="List of site IDs to include in maintenance"
    )
    
    class Meta:
        model = MaintenanceEvent
        fields = [
            'title', 'description', 'reason', 'sites', 'started_at',
            'estimated_duration', 'maintenance_message'
        ]
        extra_kwargs = {
            'title': {
                'help_text': 'Brief title describing the maintenance'
            },
            'description': {
                'help_text': 'Detailed description of the maintenance work'
            },
            'maintenance_message': {
                'help_text': 'Custom message to display during maintenance (optional)'
            }
        }
    
    def validate_sites(self, value):
        """Validate that user has access to selected sites."""
        user = self.context['request'].user
        if not user.is_staff:
            # Non-staff users can only select their own sites
            user_sites = CloudflareSite.objects.filter(owner=user)
            invalid_sites = [site for site in value if site not in user_sites]
            if invalid_sites:
                raise serializers.ValidationError(
                    f"You don't have access to sites: {[s.domain for s in invalid_sites]}"
                )
        return value
    
    def validate_estimated_duration(self, value):
        """Validate estimated duration is reasonable."""
        if value and value.total_seconds() > 24 * 3600:  # 24 hours
            raise serializers.ValidationError(
                "Estimated duration cannot exceed 24 hours"
            )
        if value and value.total_seconds() < 60:  # 1 minute
            raise serializers.ValidationError(
                "Estimated duration must be at least 1 minute"
            )
        return value


class MaintenanceEventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists."""
    
    initiated_by = serializers.StringRelatedField(read_only=True)
    affected_sites_count = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = MaintenanceEvent
        fields = [
            'id', 'title', 'reason', 'status', 'initiated_by',
            'affected_sites_count', 'duration', 'is_active',
            'started_at', 'ended_at', 'created_at'
        ]
        read_only_fields = fields


class MaintenanceEventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating MaintenanceEvent."""
    
    class Meta:
        model = MaintenanceEvent
        fields = [
            'title', 'description', 'maintenance_message', 'estimated_duration'
        ]
        
    def validate(self, data):
        """Validate that event can be updated."""
        instance = self.instance
        if instance and instance.status in [
            MaintenanceEvent.Status.COMPLETED,
            MaintenanceEvent.Status.CANCELLED,
            MaintenanceEvent.Status.FAILED
        ]:
            raise serializers.ValidationError(
                "Cannot update completed, cancelled, or failed maintenance events"
            )
        return data
