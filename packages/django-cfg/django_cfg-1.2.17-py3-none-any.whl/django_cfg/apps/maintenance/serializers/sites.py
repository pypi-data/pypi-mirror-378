"""
Site management serializers.

Serializers for CloudflareSite and SiteGroup models.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from ..models import CloudflareSite, SiteGroup
from .base import UserSerializer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Production Site',
            summary='A production Cloudflare site',
            description='Example of a production site configuration',
            value={
                'name': 'My Production Site',
                'domain': 'example.com',
                'zone_id': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
                'account_id': 'z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4',
                'api_token': 'your-cloudflare-api-token',
                'environment': 'production',
                'project': 'main-website',
                'tags': ['critical', 'ecommerce']
            }
        ),
        OpenApiExample(
            'Staging Site',
            summary='A staging environment site',
            description='Example of a staging site configuration',
            value={
                'name': 'Staging Environment',
                'domain': 'staging.example.com',
                'zone_id': 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7',
                'account_id': 'y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3',
                'api_token': 'your-cloudflare-api-token',
                'environment': 'staging',
                'project': 'main-website',
                'tags': ['testing']
            }
        )
    ]
)
class CloudflareSiteSerializer(serializers.ModelSerializer):
    """Serializer for CloudflareSite model with full details."""
    
    owner = UserSerializer(read_only=True)
    maintenance_duration = serializers.ReadOnlyField()
    health_check_endpoint = serializers.ReadOnlyField()
    is_production = serializers.ReadOnlyField()
    
    class Meta:
        model = CloudflareSite
        fields = [
            'id', 'name', 'domain', 'zone_id', 'account_id', 'api_token',
            'environment', 'project', 'tags', 'owner', 'current_status',
            'maintenance_active', 'monitoring_enabled', 'worker_name',
            'health_check_url', 'check_interval', 'failure_threshold',
            'maintenance_duration', 'health_check_endpoint', 'is_production',
            'last_maintenance_at', 'last_status_check', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'current_status', 'maintenance_duration',
            'health_check_endpoint', 'is_production', 'last_maintenance_at',
            'last_status_check', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'api_token': {'write_only': True},
            'zone_id': {
                'help_text': 'Cloudflare Zone ID (32 characters)',
                'min_length': 32,
                'max_length': 32
            },
            'account_id': {
                'help_text': 'Cloudflare Account ID (32 characters)',
                'min_length': 32,
                'max_length': 32
            },
            'name': {
                'help_text': 'Human-readable name for the site'
            },
            'domain': {
                'help_text': 'Domain name (without protocol or www)'
            },
            'environment': {
                'help_text': 'Environment type (production, staging, development, testing)'
            },
            'project': {
                'help_text': 'Project name for grouping sites'
            },
            'tags': {
                'help_text': 'List of tags for categorization'
            }
        }


class CloudflareSiteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CloudflareSite with validation."""
    
    class Meta:
        model = CloudflareSite
        fields = [
            'name', 'domain', 'zone_id', 'account_id', 'api_token',
            'environment', 'project', 'tags', 'monitoring_enabled',
            'worker_name', 'health_check_url', 'check_interval', 'failure_threshold'
        ]
        extra_kwargs = {
            'api_token': {'write_only': True},
            'zone_id': {
                'help_text': 'Cloudflare Zone ID (32 characters)',
                'min_length': 32,
                'max_length': 32
            },
            'account_id': {
                'help_text': 'Cloudflare Account ID (32 characters)', 
                'min_length': 32,
                'max_length': 32
            }
        }
    
    def validate_domain(self, value):
        """Validate domain format."""
        if value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "Domain should not include protocol (http:// or https://)"
            )
        if value.startswith('www.'):
            raise serializers.ValidationError(
                "Domain should not include www prefix"
            )
        return value.lower()
    
    def validate_zone_id(self, value):
        """Validate zone_id format."""
        if len(value) != 32:
            raise serializers.ValidationError(
                "Zone ID must be exactly 32 characters long"
            )
        return value
    
    def validate_account_id(self, value):
        """Validate account_id format."""
        if len(value) != 32:
            raise serializers.ValidationError(
                "Account ID must be exactly 32 characters long"
            )
        return value


class CloudflareSiteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for site lists."""
    
    owner = serializers.StringRelatedField(read_only=True)
    is_production = serializers.ReadOnlyField()
    
    class Meta:
        model = CloudflareSite
        fields = [
            'id', 'name', 'domain', 'environment', 'project', 'tags',
            'owner', 'current_status', 'maintenance_active', 'is_production',
            'last_maintenance_at', 'created_at'
        ]
        read_only_fields = fields


class SiteGroupSerializer(serializers.ModelSerializer):
    """Serializer for SiteGroup model."""
    
    owner = UserSerializer(read_only=True)
    sites = CloudflareSiteListSerializer(many=True, read_only=True)
    sites_count = serializers.ReadOnlyField()
    active_sites_count = serializers.ReadOnlyField()
    maintenance_sites_count = serializers.ReadOnlyField()
    
    class Meta:
        model = SiteGroup
        fields = [
            'id', 'name', 'description', 'owner', 'sites', 'sites_count',
            'active_sites_count', 'maintenance_sites_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'sites', 'sites_count', 'active_sites_count',
            'maintenance_sites_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'name': {
                'help_text': 'Name of the site group'
            },
            'description': {
                'help_text': 'Optional description of the group purpose'
            }
        }


class SiteGroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SiteGroup."""
    
    class Meta:
        model = SiteGroup
        fields = ['name', 'description']
        
    def validate_name(self, value):
        """Validate group name uniqueness for user."""
        user = self.context['request'].user
        if SiteGroup.objects.filter(owner=user, name=value).exists():
            raise serializers.ValidationError(
                "You already have a group with this name"
            )
        return value
