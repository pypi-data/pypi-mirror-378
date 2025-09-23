"""
Site management views.

ViewSets for CloudflareSite and SiteGroup management.
"""

import logging
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiResponse, OpenApiParameter, OpenApiTypes
)

from ..models import CloudflareSite, SiteGroup
from ..serializers import (
    CloudflareSiteSerializer, CloudflareSiteCreateSerializer, CloudflareSiteListSerializer,
    SiteGroupSerializer, SiteGroupCreateSerializer,
    BulkMaintenanceActionSerializer, APIResponseSerializer
)
from ..services import MaintenanceManager
from .base import MaintenancePermissionMixin, MaintenanceResponseMixin

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List Cloudflare sites",
        description="Get list of Cloudflare sites with filtering options",
        parameters=[
            OpenApiParameter('environment', OpenApiTypes.STR, description='Filter by environment'),
            OpenApiParameter('project', OpenApiTypes.STR, description='Filter by project'),
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('maintenance_active', OpenApiTypes.BOOL, description='Filter by maintenance status'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in name and domain'),
        ]
    ),
    create=extend_schema(
        summary="Create Cloudflare site",
        description="Create a new Cloudflare site configuration"
    ),
    retrieve=extend_schema(
        summary="Get Cloudflare site",
        description="Get detailed information about a specific Cloudflare site"
    ),
    update=extend_schema(
        summary="Update Cloudflare site",
        description="Update Cloudflare site configuration"
    ),
    destroy=extend_schema(
        summary="Delete Cloudflare site",
        description="Delete a Cloudflare site configuration"
    )
)
class CloudflareSiteViewSet(MaintenancePermissionMixin, MaintenanceResponseMixin, viewsets.ModelViewSet):
    """ViewSet for managing Cloudflare sites."""
    
    serializer_class = CloudflareSiteSerializer
    lookup_field = 'id'
    filterset_fields = ['environment', 'project', 'current_status', 'maintenance_active']
    search_fields = ['name', 'domain', 'project']
    ordering_fields = ['name', 'domain', 'created_at', 'last_maintenance_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset filtered by user permissions."""
        return self.get_user_queryset(CloudflareSite)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CloudflareSiteCreateSerializer
        elif self.action == 'list':
            return CloudflareSiteListSerializer
        elif self.action == 'bulk_action':
            return BulkMaintenanceActionSerializer
        return CloudflareSiteSerializer
    
    def perform_create(self, serializer):
        """Set owner when creating site."""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Enable maintenance mode",
        description="Enable maintenance mode for this site",
        request=None,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Maintenance enabled successfully"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Bad request"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        }
    )
    def enable_maintenance(self, request, id=None):
        """Enable maintenance mode for a site."""
        try:
            site = self.get_object()
            reason = request.data.get('reason', 'Manual maintenance')
            message = request.data.get('message', 'Site is under maintenance')
            
            # Use multi-site manager for consistency
            manager = MaintenanceManager(self.request.user)
            success = manager._enable_site_maintenance(site, reason, message)
            
            if success:
                return self.success_response(f'Maintenance enabled for {site.domain}')
            else:
                return self.error_response('Failed to enable maintenance mode')
                
        except Exception as e:
            return self.error_response(f"Enable maintenance error for site {id}: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Disable maintenance mode",
        description="Disable maintenance mode for this site",
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Maintenance disabled successfully"),
            500: OpenApiResponse(response=APIResponseSerializer, description="Internal server error")
        }
    )
    def disable_maintenance(self, request, id=None):
        """Disable maintenance mode for a site."""
        try:
            site = self.get_object()
            
            # Use multi-site manager for consistency
            manager = MaintenanceManager(self.request.user)
            success = manager._disable_site_maintenance(site)
            
            if success:
                return self.success_response(f'Maintenance disabled for {site.domain}')
            else:
                return self.error_response('Failed to disable maintenance mode')
                
        except Exception as e:
            return self.error_response(f"Disable maintenance error for site {id}: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Check site status",
        description="Check current status of the site",
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Status checked successfully")
        }
    )
    def check_status(self, request, id=None):
        """Check current status of a site."""
        try:
            site = self.get_object()
            
            # Use multi-site manager for consistency
            manager = MaintenanceManager(self.request.user)
            site_status = manager._check_site_status(site)
            
            return self.success_response(
                'Status checked successfully',
                data={
                    'site_id': site.id,
                    'domain': site.domain,
                    'status': site_status,
                    'maintenance_active': site.maintenance_active,
                    'last_check': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return self.error_response(f"Status check error for site {id}: {e}")
    
    @action(detail=False, methods=['post'])
    @extend_schema(
        summary="Bulk maintenance actions",
        description="Perform bulk maintenance actions on multiple sites",
        request=BulkMaintenanceActionSerializer,
        responses={
            200: OpenApiResponse(response=APIResponseSerializer, description="Bulk action completed"),
            400: OpenApiResponse(response=APIResponseSerializer, description="Invalid request data")
        }
    )
    def bulk_action(self, request):
        """Perform bulk maintenance actions."""
        serializer = BulkMaintenanceActionSerializer(data=request.data)
        if not serializer.is_valid():
            return self.validation_error_response(serializer.errors)
        
        try:
            action_type = serializer.validated_data['action']
            site_ids = serializer.validated_data['site_ids']
            dry_run = serializer.validated_data.get('dry_run', False)
            
            # Get sites (filtered by user permissions)
            sites = self.get_queryset().filter(id__in=site_ids)
            
            if dry_run:
                return self.success_response(
                    f'Dry run: would {action_type} maintenance for {sites.count()} sites',
                    data={
                        'dry_run': True,
                        'would_affect': [site.domain for site in sites]
                    }
                )
            
            # Use multi-site manager for bulk operations
            manager = MaintenanceManager(self.request.user).sites(request.user).filter(id__in=site_ids)
            
            if action_type == 'enable':
                reason = serializer.validated_data.get('reason', 'Bulk maintenance')
                result = manager.enable_maintenance(
                    reason=reason,
                    user=request.user,
                    message=serializer.validated_data.get('maintenance_message')
                )
            elif action_type == 'disable':
                result = manager.disable_maintenance(user=request.user)
            elif action_type == 'status_check':
                result = manager.check_status()
            else:
                return self.error_response(f'Unknown action: {action_type}', status.HTTP_400_BAD_REQUEST)
            
            return self.success_response(f'Bulk {action_type} completed', data=result)
            
        except Exception as e:
            return self.error_response(f"Bulk action error: {e}")


@extend_schema_view(
    list=extend_schema(
        summary="List site groups",
        description="Get list of site groups"
    ),
    create=extend_schema(
        summary="Create site group",
        description="Create a new site group"
    )
)
class SiteGroupViewSet(MaintenancePermissionMixin, MaintenanceResponseMixin, viewsets.ModelViewSet):
    """ViewSet for managing site groups."""
    
    serializer_class = SiteGroupSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get queryset filtered by user permissions."""
        return self.get_user_queryset(SiteGroup)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return SiteGroupCreateSerializer
        return SiteGroupSerializer
    
    def perform_create(self, serializer):
        """Set owner when creating group."""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Add sites to group",
        description="Add sites to this group"
    )
    def add_sites(self, request, id=None):
        """Add sites to group."""
        try:
            group = self.get_object()
            site_ids = request.data.get('site_ids', [])
            
            # Get sites (filtered by user permissions)
            sites = self.get_user_queryset(CloudflareSite).filter(id__in=site_ids)
            group.sites.add(*sites)
            
            return self.success_response(f'Added {sites.count()} sites to group {group.name}')
            
        except Exception as e:
            return self.error_response(f"Add sites to group error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Remove sites from group",
        description="Remove sites from this group"
    )
    def remove_sites(self, request, id=None):
        """Remove sites from group."""
        try:
            group = self.get_object()
            site_ids = request.data.get('site_ids', [])
            
            # Get sites (filtered by user permissions)
            sites = self.get_user_queryset(CloudflareSite).filter(id__in=site_ids)
            group.sites.remove(*sites)
            
            return self.success_response(f'Removed {sites.count()} sites from group {group.name}')
            
        except Exception as e:
            return self.error_response(f"Remove sites from group error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Enable maintenance for group",
        description="Enable maintenance mode for all sites in this group"
    )
    def enable_maintenance(self, request, id=None):
        """Enable maintenance for all sites in group."""
        try:
            group = self.get_object()
            reason = request.data.get('reason', f'Group maintenance: {group.name}')
            
            result = group.enable_maintenance_for_all(request.user, reason)
            
            return self.success_response(
                f'Group maintenance enabled for {group.name}',
                data=result
            )
            
        except Exception as e:
            return self.error_response(f"Group maintenance enable error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Disable maintenance for group",
        description="Disable maintenance mode for all sites in this group"
    )
    def disable_maintenance(self, request, id=None):
        """Disable maintenance for all sites in group."""
        try:
            group = self.get_object()
            
            result = group.disable_maintenance_for_all()
            
            return self.success_response(
                f'Group maintenance disabled for {group.name}',
                data=result
            )
            
        except Exception as e:
            return self.error_response(f"Group maintenance disable error: {e}")
