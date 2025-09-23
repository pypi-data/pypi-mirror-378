"""
Monitoring serializers.

Serializers for MonitoringTarget and HealthCheckResult models.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from ..models import MonitoringTarget, HealthCheckResult
from .sites import CloudflareSiteListSerializer


class HealthCheckResultSerializer(serializers.ModelSerializer):
    """Serializer for HealthCheckResult model."""
    
    class Meta:
        model = HealthCheckResult
        fields = [
            'id', 'target', 'success', 'status_code', 'response_time_ms',
            'error_message', 'response_headers', 'timestamp'
        ]
        read_only_fields = fields
        extra_kwargs = {
            'success': {
                'help_text': 'Whether the health check was successful'
            },
            'status_code': {
                'help_text': 'HTTP status code returned'
            },
            'response_time_ms': {
                'help_text': 'Response time in milliseconds'
            },
            'error_message': {
                'help_text': 'Error message if check failed'
            },
            'response_headers': {
                'help_text': 'Response headers as JSON'
            }
        }


class HealthCheckResultListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for health check result lists."""
    
    class Meta:
        model = HealthCheckResult
        fields = [
            'id', 'success', 'status_code', 'response_time_ms', 'timestamp'
        ]
        read_only_fields = fields


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Basic Monitoring Target',
            summary='A basic monitoring configuration',
            description='Example of a basic monitoring target for a production site',
            value={
                'check_url': 'https://example.com/health/',
                'expected_status_codes': [200, 201],
                'timeout_seconds': 10,
                'check_interval_seconds': 60,
                'failure_threshold': 3,
                'recovery_threshold': 2
            }
        ),
        OpenApiExample(
            'Advanced Monitoring Target',
            summary='An advanced monitoring configuration',
            description='Example with custom headers and SSL verification',
            value={
                'check_url': 'https://api.example.com/status',
                'expected_status_codes': [200],
                'timeout_seconds': 15,
                'check_interval_seconds': 30,
                'failure_threshold': 5,
                'recovery_threshold': 3,
                'custom_headers': {
                    'Authorization': 'Bearer token123',
                    'User-Agent': 'Maintenance-Monitor/1.0'
                },
                'follow_redirects': True,
                'verify_ssl': True,
                'expected_response_time_ms': 2000
            }
        )
    ]
)
class MonitoringTargetSerializer(serializers.ModelSerializer):
    """Serializer for MonitoringTarget model."""
    
    site = CloudflareSiteListSerializer(read_only=True)
    results = HealthCheckResultListSerializer(many=True, read_only=True)
    recent_results = serializers.SerializerMethodField()
    uptime_percentage = serializers.SerializerMethodField()
    average_response_time = serializers.SerializerMethodField()
    
    class Meta:
        model = MonitoringTarget
        fields = [
            'id', 'site', 'status', 'check_url', 'expected_status_codes',
            'timeout_seconds', 'check_interval_seconds', 'failure_threshold',
            'recovery_threshold', 'custom_headers', 'follow_redirects',
            'verify_ssl', 'expected_response_time_ms', 'results',
            'recent_results', 'uptime_percentage', 'average_response_time',
            'last_check_at', 'consecutive_failures', 'consecutive_successes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'site', 'results', 'recent_results', 'uptime_percentage',
            'average_response_time', 'last_check_at', 'consecutive_failures',
            'consecutive_successes', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'check_url': {
                'help_text': 'URL to monitor for health checks'
            },
            'expected_status_codes': {
                'help_text': 'List of HTTP status codes considered successful'
            },
            'timeout_seconds': {
                'help_text': 'Request timeout in seconds'
            },
            'check_interval_seconds': {
                'help_text': 'Interval between checks in seconds'
            },
            'failure_threshold': {
                'help_text': 'Number of consecutive failures before marking as down'
            },
            'recovery_threshold': {
                'help_text': 'Number of consecutive successes before marking as up'
            },
            'custom_headers': {
                'help_text': 'Custom HTTP headers to send with requests'
            },
            'expected_response_time_ms': {
                'help_text': 'Expected response time threshold in milliseconds'
            }
        }
    
    def get_recent_results(self, obj):
        """Get recent health check results (last 10)."""
        recent = obj.results.order_by('-timestamp')[:10]
        return HealthCheckResultListSerializer(recent, many=True).data
    
    def get_uptime_percentage(self, obj):
        """Calculate uptime percentage over last 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get results from last 24 hours
        since = timezone.now() - timedelta(hours=24)
        recent_results = obj.results.filter(timestamp__gte=since)
        
        if not recent_results.exists():
            return None
        
        total_checks = recent_results.count()
        successful_checks = recent_results.filter(success=True).count()
        
        return round((successful_checks / total_checks) * 100, 2)
    
    def get_average_response_time(self, obj):
        """Calculate average response time over last 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg
        
        # Get results from last 24 hours
        since = timezone.now() - timedelta(hours=24)
        recent_results = obj.results.filter(
            timestamp__gte=since,
            success=True,
            response_time_ms__isnull=False
        )
        
        if not recent_results.exists():
            return None
        
        avg_time = recent_results.aggregate(
            avg=Avg('response_time_ms')
        )['avg']
        
        return round(avg_time, 2) if avg_time else None


class MonitoringTargetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MonitoringTarget."""
    
    class Meta:
        model = MonitoringTarget
        fields = [
            'check_url', 'expected_status_codes', 'timeout_seconds',
            'check_interval_seconds', 'failure_threshold', 'recovery_threshold',
            'custom_headers', 'follow_redirects', 'verify_ssl',
            'expected_response_time_ms'
        ]
    
    def validate_check_url(self, value):
        """Validate check URL format."""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "Check URL must start with http:// or https://"
            )
        return value
    
    def validate_expected_status_codes(self, value):
        """Validate status codes."""
        if not value:
            raise serializers.ValidationError(
                "At least one expected status code is required"
            )
        
        for code in value:
            if not (100 <= code <= 599):
                raise serializers.ValidationError(
                    f"Invalid HTTP status code: {code}"
                )
        
        return value
    
    def validate_timeout_seconds(self, value):
        """Validate timeout is reasonable."""
        if value < 1:
            raise serializers.ValidationError(
                "Timeout must be at least 1 second"
            )
        if value > 300:
            raise serializers.ValidationError(
                "Timeout cannot exceed 300 seconds"
            )
        return value
    
    def validate_check_interval_seconds(self, value):
        """Validate check interval is reasonable."""
        if value < 10:
            raise serializers.ValidationError(
                "Check interval must be at least 10 seconds"
            )
        if value > 3600:
            raise serializers.ValidationError(
                "Check interval cannot exceed 3600 seconds (1 hour)"
            )
        return value


class MonitoringTargetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for monitoring target lists."""
    
    site = serializers.StringRelatedField(read_only=True)
    uptime_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = MonitoringTarget
        fields = [
            'id', 'site', 'status', 'check_url', 'uptime_percentage',
            'last_check_at', 'consecutive_failures', 'consecutive_successes'
        ]
        read_only_fields = fields
    
    def get_uptime_percentage(self, obj):
        """Calculate uptime percentage over last 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get results from last 24 hours
        since = timezone.now() - timedelta(hours=24)
        recent_results = obj.results.filter(timestamp__gte=since)
        
        if not recent_results.exists():
            return None
        
        total_checks = recent_results.count()
        successful_checks = recent_results.filter(success=True).count()
        
        return round((successful_checks / total_checks) * 100, 2)
