"""
Cloudflare deployment views.

ViewSets for CloudflareDeployment management.
"""

import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

from ..models import CloudflareDeployment
from ..serializers import (
    CloudflareDeploymentSerializer, CloudflareDeploymentListSerializer
)
from .base import MaintenancePermissionMixin, MaintenanceResponseMixin

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List Cloudflare deployments",
        description="Get list of Cloudflare deployments"
    ),
    retrieve=extend_schema(
        summary="Get Cloudflare deployment",
        description="Get detailed information about a Cloudflare deployment"
    ),
    destroy=extend_schema(
        summary="Delete Cloudflare deployment",
        description="Delete a Cloudflare deployment record"
    )
)
class CloudflareDeploymentViewSet(MaintenancePermissionMixin, MaintenanceResponseMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing Cloudflare deployments (read-only)."""
    
    serializer_class = CloudflareDeploymentSerializer
    lookup_field = 'id'
    filterset_fields = ['deployment_type', 'status']
    ordering = ['-deployed_at']
    
    def get_queryset(self):
        """Get queryset filtered by user permissions."""
        # CloudflareDeployment is related to CloudflareSite via site.owner
        if getattr(self, 'swagger_fake_view', False):
            return CloudflareDeployment.objects.none()
        
        user = self.request.user
        if user.is_staff:
            return CloudflareDeployment.objects.all()
        
        return CloudflareDeployment.objects.filter(site__owner=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return CloudflareDeploymentListSerializer
        return CloudflareDeploymentSerializer
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Rollback deployment",
        description="Rollback this Cloudflare deployment"
    )
    def rollback(self, request, id=None):
        """Rollback a deployment."""
        try:
            deployment = self.get_object()
            
            if deployment.status != CloudflareDeployment.Status.ACTIVE:
                return self.error_response(
                    f'Cannot rollback deployment with status: {deployment.status}',
                    status_code=400
                )
            
            # Import Cloudflare service
            from ..services.cloudflare_service import CloudflareService
            
            cloudflare_service = CloudflareService()
            success = cloudflare_service.rollback_deployment(deployment)
            
            if success:
                deployment.status = CloudflareDeployment.Status.ROLLED_BACK
                deployment.save()
                
                return self.success_response(f'Deployment {deployment.id} rolled back successfully')
            else:
                return self.error_response('Failed to rollback deployment')
                
        except Exception as e:
            return self.error_response(f"Rollback deployment error: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get deployment logs",
        description="Get logs for this deployment"
    )
    def logs(self, request, id=None):
        """Get logs for a deployment."""
        try:
            deployment = self.get_object()
            
            # Import Cloudflare service
            from ..services.cloudflare_service import CloudflareService
            
            cloudflare_service = CloudflareService()
            logs = cloudflare_service.get_deployment_logs(deployment)
            
            return self.success_response(
                f'Retrieved logs for deployment {deployment.id}',
                data={'logs': logs}
            )
            
        except Exception as e:
            return self.error_response(f"Get deployment logs error: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get deployment status",
        description="Get current status of this deployment from Cloudflare"
    )
    def status(self, request, id=None):
        """Get current deployment status from Cloudflare."""
        try:
            deployment = self.get_object()
            
            # Import Cloudflare service
            from ..services.cloudflare_service import CloudflareService
            
            cloudflare_service = CloudflareService()
            status_info = cloudflare_service.get_deployment_status(deployment)
            
            return self.success_response(
                f'Retrieved status for deployment {deployment.id}',
                data=status_info
            )
            
        except Exception as e:
            return self.error_response(f"Get deployment status error: {e}")
    
    @action(detail=False, methods=['get'])
    @extend_schema(
        summary="Get deployment statistics",
        description="Get deployment statistics for user's sites"
    )
    def statistics(self, request):
        """Get deployment statistics."""
        try:
            deployments = self.get_queryset()
            
            stats = {
                'total_deployments': deployments.count(),
                'active_deployments': deployments.filter(status=CloudflareDeployment.Status.ACTIVE).count(),
                'failed_deployments': deployments.filter(status=CloudflareDeployment.Status.FAILED).count(),
                'rolled_back_deployments': deployments.filter(status=CloudflareDeployment.Status.ROLLED_BACK).count(),
                'by_type': {},
                'recent_deployments': []
            }
            
            # Count by deployment type
            for deployment_type in CloudflareDeployment.DeploymentType.choices:
                type_value = deployment_type[0]
                count = deployments.filter(deployment_type=type_value).count()
                stats['by_type'][type_value] = count
            
            # Get recent deployments
            recent = deployments.order_by('-deployed_at')[:10]
            serializer = CloudflareDeploymentListSerializer(recent, many=True)
            stats['recent_deployments'] = serializer.data
            
            return self.success_response('Deployment statistics retrieved', data=stats)
            
        except Exception as e:
            return self.error_response(f"Get deployment statistics error: {e}")
