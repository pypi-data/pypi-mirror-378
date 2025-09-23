"""
Maintenance event views.

ViewSets for MaintenanceEvent management.
"""

import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

from ..models import MaintenanceEvent
from ..serializers import (
    MaintenanceEventSerializer, MaintenanceEventCreateSerializer, MaintenanceEventListSerializer,
    MaintenanceEventUpdateSerializer
)
from .base import MaintenancePermissionMixin, MaintenanceResponseMixin

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List maintenance events",
        description="Get list of maintenance events"
    ),
    create=extend_schema(
        summary="Create maintenance event",
        description="Create a new maintenance event"
    ),
    retrieve=extend_schema(
        summary="Get maintenance event",
        description="Get detailed information about a maintenance event"
    ),
    update=extend_schema(
        summary="Update maintenance event",
        description="Update maintenance event details"
    ),
    destroy=extend_schema(
        summary="Delete maintenance event",
        description="Delete a maintenance event"
    )
)
class MaintenanceEventViewSet(MaintenancePermissionMixin, MaintenanceResponseMixin, viewsets.ModelViewSet):
    """ViewSet for managing maintenance events."""
    
    serializer_class = MaintenanceEventSerializer
    lookup_field = 'id'
    filterset_fields = ['status', 'reason']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset filtered by user permissions."""
        return self.get_user_queryset(MaintenanceEvent, 'initiated_by')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return MaintenanceEventCreateSerializer
        elif self.action == 'list':
            return MaintenanceEventListSerializer
        elif self.action in ['update', 'partial_update']:
            return MaintenanceEventUpdateSerializer
        return MaintenanceEventSerializer
    
    def perform_create(self, serializer):
        """Set initiated_by when creating event."""
        serializer.save(initiated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Complete maintenance event",
        description="Mark maintenance event as completed"
    )
    def complete(self, request, id=None):
        """Complete a maintenance event."""
        try:
            event = self.get_object()
            
            if event.status != MaintenanceEvent.Status.ACTIVE:
                return self.error_response(
                    f'Cannot complete event with status: {event.status}',
                    status_code=400
                )
            
            event.complete(request.user)
            
            return self.success_response(f'Maintenance event "{event.title}" completed')
            
        except Exception as e:
            return self.error_response(f"Complete maintenance event error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Cancel maintenance event",
        description="Cancel maintenance event"
    )
    def cancel(self, request, id=None):
        """Cancel a maintenance event."""
        try:
            event = self.get_object()
            
            if event.status not in [MaintenanceEvent.Status.ACTIVE, MaintenanceEvent.Status.SCHEDULED]:
                return self.error_response(
                    f'Cannot cancel event with status: {event.status}',
                    status_code=400
                )
            
            event.cancel(request.user)
            
            return self.success_response(f'Maintenance event "{event.title}" cancelled')
            
        except Exception as e:
            return self.error_response(f"Cancel maintenance event error: {e}")
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Fail maintenance event",
        description="Mark maintenance event as failed"
    )
    def fail(self, request, id=None):
        """Mark a maintenance event as failed."""
        try:
            event = self.get_object()
            error_message = request.data.get('error_message', 'Maintenance failed')
            
            if event.status != MaintenanceEvent.Status.ACTIVE:
                return self.error_response(
                    f'Cannot fail event with status: {event.status}',
                    status_code=400
                )
            
            event.fail(error_message)
            
            return self.success_response(f'Maintenance event "{event.title}" marked as failed')
            
        except Exception as e:
            return self.error_response(f"Fail maintenance event error: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get event logs",
        description="Get logs for this maintenance event"
    )
    def logs(self, request, id=None):
        """Get logs for a maintenance event."""
        try:
            event = self.get_object()
            logs = event.logs.order_by('-timestamp')
            
            # Simple pagination
            page_size = int(request.query_params.get('page_size', 50))
            page = int(request.query_params.get('page', 1))
            start = (page - 1) * page_size
            end = start + page_size
            
            paginated_logs = logs[start:end]
            
            from ..serializers import MaintenanceLogSerializer
            serializer = MaintenanceLogSerializer(paginated_logs, many=True)
            
            return self.success_response(
                f'Retrieved {len(serializer.data)} logs',
                data={
                    'logs': serializer.data,
                    'total': logs.count(),
                    'page': page,
                    'page_size': page_size
                }
            )
            
        except Exception as e:
            return self.error_response(f"Get event logs error: {e}")
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        summary="Get event statistics",
        description="Get statistics for this maintenance event"
    )
    def statistics(self, request, id=None):
        """Get statistics for a maintenance event."""
        try:
            event = self.get_object()
            
            stats = {
                'event_id': event.id,
                'title': event.title,
                'status': event.status,
                'duration': event.duration.total_seconds() if event.duration else None,
                'affected_sites': event.affected_sites_count,
                'success_count': event.success_count,
                'error_count_before': event.error_count_before,
                'error_count_during': event.error_count_during,
                'is_active': event.is_active,
                'is_scheduled': event.is_scheduled,
                'started_at': event.started_at.isoformat() if event.started_at else None,
                'ended_at': event.ended_at.isoformat() if event.ended_at else None,
                'logs_count': event.logs.count()
            }
            
            return self.success_response('Event statistics retrieved', data=stats)
            
        except Exception as e:
            return self.error_response(f"Get event statistics error: {e}")
