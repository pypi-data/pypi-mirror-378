"""
Action serializers.

Serializers for bulk operations and filtering.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from ..models import CloudflareSite


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Enable Maintenance',
            summary='Enable maintenance for multiple sites',
            description='Example of enabling maintenance mode for selected sites',
            value={
                'action': 'enable',
                'site_ids': [1, 2, 3],
                'reason': 'Database migration',
                'maintenance_message': 'We are performing scheduled maintenance. Please try again in 2 hours.',
                'estimated_duration': '02:00:00',
                'dry_run': False
            }
        ),
        OpenApiExample(
            'Disable Maintenance',
            summary='Disable maintenance for multiple sites',
            description='Example of disabling maintenance mode',
            value={
                'action': 'disable',
                'site_ids': [1, 2, 3],
                'dry_run': False
            }
        ),
        OpenApiExample(
            'Status Check',
            summary='Check status of multiple sites',
            description='Example of checking status for multiple sites',
            value={
                'action': 'status_check',
                'site_ids': [1, 2, 3, 4, 5]
            }
        ),
        OpenApiExample(
            'Dry Run',
            summary='Dry run operation',
            description='Example of a dry run to see what would be affected',
            value={
                'action': 'enable',
                'site_ids': [1, 2, 3],
                'reason': 'Test maintenance',
                'dry_run': True
            }
        )
    ]
)
class BulkMaintenanceActionSerializer(serializers.Serializer):
    """Serializer for bulk maintenance actions."""
    
    action = serializers.ChoiceField(
        choices=['enable', 'disable', 'status_check'],
        help_text="Action to perform on selected sites"
    )
    site_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=100,
        help_text="List of site IDs to perform action on (max 100)"
    )
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for maintenance (required for enable action)"
    )
    maintenance_message = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Custom maintenance message to display"
    )
    estimated_duration = serializers.DurationField(
        required=False,
        help_text="Estimated maintenance duration (HH:MM:SS format)"
    )
    dry_run = serializers.BooleanField(
        default=False,
        help_text="Perform a dry run without making actual changes"
    )
    
    def validate(self, data):
        """Validate bulk action data."""
        action = data['action']
        
        # Reason is required for enable action
        if action == 'enable' and not data.get('reason'):
            raise serializers.ValidationError({
                'reason': 'Reason is required when enabling maintenance'
            })
        
        # Validate estimated duration
        if data.get('estimated_duration'):
            duration = data['estimated_duration']
            if duration.total_seconds() > 24 * 3600:  # 24 hours
                raise serializers.ValidationError({
                    'estimated_duration': 'Duration cannot exceed 24 hours'
                })
            if duration.total_seconds() < 60:  # 1 minute
                raise serializers.ValidationError({
                    'estimated_duration': 'Duration must be at least 1 minute'
                })
        
        return data
    
    def validate_site_ids(self, value):
        """Validate site IDs exist and are accessible."""
        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(value))
        
        if len(unique_ids) != len(value):
            raise serializers.ValidationError(
                "Duplicate site IDs are not allowed"
            )
        
        # Check if sites exist (will be further filtered by permissions in view)
        existing_sites = CloudflareSite.objects.filter(id__in=unique_ids)
        existing_ids = set(existing_sites.values_list('id', flat=True))
        missing_ids = set(unique_ids) - existing_ids
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Sites not found: {sorted(missing_ids)}"
            )
        
        return unique_ids


class SiteFilterSerializer(serializers.Serializer):
    """Serializer for site filtering parameters."""
    
    environment = serializers.ChoiceField(
        choices=CloudflareSite.SiteEnvironment.choices,
        required=False,
        help_text="Filter by environment"
    )
    project = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Filter by project name"
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Filter by tags (sites must have ALL specified tags)"
    )
    status = serializers.ChoiceField(
        choices=CloudflareSite.SiteStatus.choices,
        required=False,
        help_text="Filter by current status"
    )
    maintenance_active = serializers.BooleanField(
        required=False,
        help_text="Filter by maintenance status"
    )
    monitoring_enabled = serializers.BooleanField(
        required=False,
        help_text="Filter by monitoring status"
    )
    owner_id = serializers.IntegerField(
        required=False,
        help_text="Filter by owner ID (staff only)"
    )
    
    def validate_tags(self, value):
        """Validate tags format."""
        if value:
            # Remove duplicates and empty strings
            cleaned_tags = [tag.strip() for tag in value if tag.strip()]
            if len(cleaned_tags) != len(value):
                raise serializers.ValidationError(
                    "Tags cannot be empty or contain only whitespace"
                )
            return cleaned_tags
        return value


class BulkOperationResultSerializer(serializers.Serializer):
    """Serializer for bulk operation results."""
    
    total = serializers.IntegerField(help_text="Total number of sites processed")
    successful = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of successfully processed site domains"
    )
    failed = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of failed operations with details"
    )
    skipped = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of skipped operations with reasons"
    )
    dry_run = serializers.BooleanField(
        default=False,
        help_text="Whether this was a dry run"
    )
    would_affect = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Sites that would be affected (dry run only)"
    )
    execution_time = serializers.FloatField(
        required=False,
        help_text="Execution time in seconds"
    )


class SiteGroupActionSerializer(serializers.Serializer):
    """Serializer for site group actions."""
    
    action = serializers.ChoiceField(
        choices=['add_sites', 'remove_sites', 'enable_maintenance', 'disable_maintenance'],
        help_text="Action to perform on the group"
    )
    site_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="Site IDs for add/remove actions"
    )
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for maintenance actions"
    )
    maintenance_message = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Custom maintenance message"
    )
    
    def validate(self, data):
        """Validate group action data."""
        action = data['action']
        
        # Site IDs required for add/remove actions
        if action in ['add_sites', 'remove_sites'] and not data.get('site_ids'):
            raise serializers.ValidationError({
                'site_ids': f'Site IDs are required for {action} action'
            })
        
        # Reason required for enable maintenance
        if action == 'enable_maintenance' and not data.get('reason'):
            raise serializers.ValidationError({
                'reason': 'Reason is required for enable maintenance action'
            })
        
        return data


class MaintenanceScheduleSerializer(serializers.Serializer):
    """Serializer for scheduling maintenance."""
    
    scheduled_at = serializers.DateTimeField(
        help_text="When to start the maintenance"
    )
    site_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        help_text="Sites to include in scheduled maintenance"
    )
    title = serializers.CharField(
        max_length=200,
        help_text="Maintenance title"
    )
    description = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Detailed description"
    )
    estimated_duration = serializers.DurationField(
        help_text="Estimated maintenance duration"
    )
    maintenance_message = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Message to display during maintenance"
    )
    notify_users = serializers.BooleanField(
        default=True,
        help_text="Whether to notify users about scheduled maintenance"
    )
    
    def validate_scheduled_at(self, value):
        """Validate scheduled time is in the future."""
        from django.utils import timezone
        
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future"
            )
        
        # Don't allow scheduling too far in the future (1 year)
        max_future = timezone.now() + timezone.timedelta(days=365)
        if value > max_future:
            raise serializers.ValidationError(
                "Cannot schedule maintenance more than 1 year in advance"
            )
        
        return value
