"""
Deployment serializers.

Serializers for CloudflareDeployment model.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from ..models import CloudflareDeployment
from .sites import CloudflareSiteListSerializer
from .events import MaintenanceEventListSerializer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Worker Deployment',
            summary='A Cloudflare Worker deployment',
            description='Example of a successful Worker deployment',
            value={
                'id': 1,
                'deployment_type': 'worker',
                'resource_name': 'maintenance-mode',
                'resource_id': 'worker123',
                'status': 'deployed',
                'script_content': 'addEventListener("fetch", event => { ... })',
                'is_active': True,
                'can_rollback': True
            }
        ),
        OpenApiExample(
            'Failed Deployment',
            summary='A failed deployment',
            description='Example of a deployment that failed',
            value={
                'id': 2,
                'deployment_type': 'worker',
                'resource_name': 'maintenance-mode',
                'status': 'failed',
                'error_message': 'Script validation failed: Invalid syntax',
                'is_active': False,
                'can_rollback': False
            }
        )
    ]
)
class CloudflareDeploymentSerializer(serializers.ModelSerializer):
    """Serializer for CloudflareDeployment model with full details."""
    
    site = CloudflareSiteListSerializer(read_only=True)
    maintenance_event = MaintenanceEventListSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    can_rollback = serializers.ReadOnlyField()
    deployment_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = CloudflareDeployment
        fields = [
            'id', 'site', 'deployment_type', 'resource_name', 'resource_id',
            'status', 'maintenance_event', 'script_content', 'configuration_data',
            'rollback_data', 'error_message', 'is_active', 'can_rollback',
            'deployment_duration', 'created_at', 'deployed_at', 'failed_at', 'rolled_back_at'
        ]
        read_only_fields = [
            'id', 'site', 'maintenance_event', 'resource_id', 'status',
            'error_message', 'is_active', 'can_rollback', 'deployment_duration',
            'created_at', 'deployed_at', 'failed_at', 'rolled_back_at'
        ]
        extra_kwargs = {
            'deployment_type': {
                'help_text': 'Type of Cloudflare resource (worker, page_rule, dns_record, etc.)'
            },
            'resource_name': {
                'help_text': 'Name of the deployed resource'
            },
            'resource_id': {
                'help_text': 'Cloudflare resource ID (set after deployment)'
            },
            'script_content': {
                'help_text': 'Worker script content (for worker deployments)'
            },
            'configuration_data': {
                'help_text': 'Configuration data as JSON'
            },
            'rollback_data': {
                'help_text': 'Data needed for rollback operations'
            }
        }
    
    def get_deployment_duration(self, obj):
        """Calculate deployment duration if available."""
        if obj.deployed_at and obj.created_at:
            duration = obj.deployed_at - obj.created_at
            return duration.total_seconds()
        return None


class CloudflareDeploymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for deployment lists."""
    
    site = serializers.StringRelatedField(read_only=True)
    maintenance_event = serializers.StringRelatedField(read_only=True)
    is_active = serializers.ReadOnlyField()
    can_rollback = serializers.ReadOnlyField()
    
    class Meta:
        model = CloudflareDeployment
        fields = [
            'id', 'site', 'deployment_type', 'resource_name', 'status',
            'maintenance_event', 'is_active', 'can_rollback',
            'created_at', 'deployed_at'
        ]
        read_only_fields = fields


class CloudflareDeploymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CloudflareDeployment."""
    
    class Meta:
        model = CloudflareDeployment
        fields = [
            'deployment_type', 'resource_name', 'script_content',
            'configuration_data', 'rollback_data'
        ]
        extra_kwargs = {
            'script_content': {
                'help_text': 'JavaScript code for Worker deployments'
            },
            'configuration_data': {
                'help_text': 'Configuration as JSON object'
            },
            'rollback_data': {
                'help_text': 'Rollback configuration as JSON object'
            }
        }
    
    def validate_script_content(self, value):
        """Validate Worker script content."""
        if self.initial_data.get('deployment_type') == 'worker' and not value:
            raise serializers.ValidationError(
                "Script content is required for Worker deployments"
            )
        
        if value and len(value) > 1024 * 1024:  # 1MB limit
            raise serializers.ValidationError(
                "Script content cannot exceed 1MB"
            )
        
        return value
    
    def validate_resource_name(self, value):
        """Validate resource name format."""
        import re
        
        if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
            raise serializers.ValidationError(
                "Resource name can only contain letters, numbers, hyphens, and underscores"
            )
        
        if len(value) > 100:
            raise serializers.ValidationError(
                "Resource name cannot exceed 100 characters"
            )
        
        return value


class DeploymentStatusSerializer(serializers.Serializer):
    """Serializer for deployment status responses."""
    
    deployment_id = serializers.IntegerField(help_text="Deployment ID")
    status = serializers.ChoiceField(
        choices=CloudflareDeployment.Status.choices,
        help_text="Current deployment status"
    )
    is_active = serializers.BooleanField(help_text="Whether deployment is active")
    can_rollback = serializers.BooleanField(help_text="Whether deployment can be rolled back")
    resource_id = serializers.CharField(
        required=False,
        help_text="Cloudflare resource ID (if deployed)"
    )
    error_message = serializers.CharField(
        required=False,
        help_text="Error message (if failed)"
    )
    deployed_at = serializers.DateTimeField(
        required=False,
        help_text="Deployment timestamp"
    )


class RollbackRequestSerializer(serializers.Serializer):
    """Serializer for rollback requests."""
    
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for rollback"
    )
    force = serializers.BooleanField(
        default=False,
        help_text="Force rollback even if risky"
    )
    
    def validate(self, data):
        """Validate rollback request."""
        # Additional validation can be added here
        return data
