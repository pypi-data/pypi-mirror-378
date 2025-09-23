"""
Monitoring views.

ViewSets for MonitoringTarget management.
"""

import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

from ..models import MonitoringTarget
from ..serializers import (
    MonitoringTargetSerializer, MonitoringTargetCreateSerializer,
    HealthCheckResultSerializer
)
from .base import MaintenancePermissionMixin, MaintenanceResponseMixin

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List monitoring targets",
        description="Get list of monitoring targets"
    ),
    create=extend_schema(
        summary="Create monitoring target",
        description="Create a new monitoring target"
    ),
    retrieve=extend_schema(
        summary="Get monitoring target",
        description="Get detailed information about a monitoring target"
    ),
    update=extend_schema(
        summary="Update monitoring target",
        description="Update monitoring target configuration"
    ),
    destroy=extend_schema(
        summary="Delete monitoring target",
        description="Delete a monitoring target"
    )
)
class MonitoringTargetViewSet(MaintenancePermissionMixin, MaintenanceResponseMixin, viewsets.ModelViewSet):
    """ViewSet for managing monitoring targets."""
    
    serializer_class = MonitoringTargetSerializer
    lookup_field = 'id'
    filterset_fields = ['is_active', 'check_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset filtered by user permissions."""
        # MonitoringTarget is related to CloudflareSite via site.owner
        if getattr(self, 'swagger_fake_view', False):
            return MonitoringTarget.objects.none()
        
        user = self.request.user
        if user.is_staff:
            return MonitoringTarget.objects.all()
        
        return MonitoringTarget.objects.filter(site__owner=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return MonitoringTargetCreateSerializer
        return MonitoringTargetSerializer
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Run health check",
        description="Run health check for this monitoring target",
        responses={
            200: HealthCheckResultSerializer
        }
    )
    def health_check(self, request, id=None):
        """Run health check for a monitoring target."""
        try:
            target = self.get_object()
            
            # Import monitoring service
            from ..services.monitoring_service import MonitoringService
            
            monitoring_service = MonitoringService()
            result = monitoring_service.check_target_health(target)
            
            # Serialize the result
            serializer = HealthCheckResultSerializer(result)
            
            return self.success_response(
                f'Health check completed for {target.site.domain}',
                data=serializer.data
            )
            
        except Exception as e:
            return self.error_response(f"Health check error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Enable monitoring",
        description="Enable monitoring for this target"
    )
    def enable(self, request, id=None):
        """Enable monitoring for a target."""
        try:
            target = self.get_object()
            target.is_active = True
            target.save()
            
            return self.success_response(f'Monitoring enabled for {target.site.domain}')
            
        except Exception as e:
            return self.error_response(f"Enable monitoring error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Disable monitoring",
        description="Disable monitoring for this target"
    )
    def disable(self, request, id=None):
        """Disable monitoring for a target."""
        try:
            target = self.get_object()
            target.is_active = False
            target.save()
            
            return self.success_response(f'Monitoring disabled for {target.site.domain}')
            
        except Exception as e:
            return self.error_response(f"Disable monitoring error: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get monitoring statistics",
        description="Get monitoring statistics for this target"
    )
    def statistics(self, request, id=None):
        """Get monitoring statistics for a target."""
        try:
            target = self.get_object()
            
            stats = {
                'target_id': target.id,
                'site_domain': target.site.domain,
                'is_active': target.is_active,
                'check_type': target.check_type,
                'check_interval': target.check_interval,
                'timeout': target.timeout,
                'retry_count': target.retry_count,
                'last_check': target.last_check.isoformat() if target.last_check else None,
                'last_status': target.last_status,
                'consecutive_failures': target.consecutive_failures,
                'total_checks': target.total_checks,
                'total_failures': target.total_failures,
                'uptime_percentage': target.uptime_percentage,
                'created_at': target.created_at.isoformat(),
                'updated_at': target.updated_at.isoformat()
            }
            
            return self.success_response('Monitoring statistics retrieved', data=stats)
            
        except Exception as e:
            return self.error_response(f"Get monitoring statistics error: {e}")
    
    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Run bulk health checks",
        description="Run health checks for multiple monitoring targets"
    )
    def bulk_health_check(self, request):
        """Run health checks for multiple targets."""
        try:
            target_ids = request.data.get('target_ids', [])
            
            if not target_ids:
                return self.error_response('No target IDs provided', status_code=400)
            
            # Get targets (filtered by user permissions)
            targets = self.get_queryset().filter(id__in=target_ids)
            
            # Import monitoring service
            from ..services.monitoring_service import MonitoringService
            
            monitoring_service = MonitoringService()
            results = []
            
            for target in targets:
                try:
                    result = monitoring_service.check_target_health(target)
                    serializer = HealthCheckResultSerializer(result)
                    results.append({
                        'target_id': target.id,
                        'domain': target.site.domain,
                        'success': True,
                        'result': serializer.data
                    })
                except Exception as e:
                    results.append({
                        'target_id': target.id,
                        'domain': target.site.domain,
                        'success': False,
                        'error': str(e)
                    })
            
            return self.success_response(
                f'Bulk health check completed for {len(results)} targets',
                data={'results': results}
            )
            
        except Exception as e:
            return self.error_response(f"Bulk health check error: {e}")
