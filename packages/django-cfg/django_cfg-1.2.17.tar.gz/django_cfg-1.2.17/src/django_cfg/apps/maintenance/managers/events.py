"""
Custom managers for maintenance event models.

Provides enhanced querying capabilities for MaintenanceEvent and MaintenanceLog models.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any, List
from datetime import timedelta


class MaintenanceEventQuerySet(models.QuerySet):
    """Custom queryset for MaintenanceEvent."""
    
    def for_user(self, user):
        """Filter events initiated by specific user."""
        return self.filter(initiated_by=user)
    
    def by_status(self, status: str):
        """Filter by event status."""
        return self.filter(status=status)
    
    def by_reason(self, reason: str):
        """Filter by maintenance reason."""
        return self.filter(reason__icontains=reason)
    
    def active(self):
        """Get currently active maintenance events."""
        return self.filter(status='active')
    
    def completed(self):
        """Get completed maintenance events."""
        return self.filter(status='completed')
    
    def failed(self):
        """Get failed maintenance events."""
        return self.filter(status='failed')
    
    def cancelled(self):
        """Get cancelled maintenance events."""
        return self.filter(status='cancelled')
    
    def scheduled(self):
        """Get scheduled maintenance events."""
        return self.filter(status='scheduled')
    
    def recent(self, days: int = 7):
        """Get recent maintenance events."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def long_running(self, hours: int = 2):
        """Get long-running maintenance events."""
        cutoff = timezone.now() - timedelta(hours=hours)
        return self.filter(
            status='active',
            started_at__lte=cutoff
        )
    
    def with_sites(self):
        """Include related sites in query."""
        return self.prefetch_related('sites')
    
    def with_logs(self):
        """Include related logs in query."""
        return self.prefetch_related('logs')
    
    def with_deployments(self):
        """Include related Cloudflare deployments."""
        return self.prefetch_related('cloudflare_deployments')
    
    def with_full_relations(self):
        """Include all related objects."""
        return self.select_related('initiated_by').prefetch_related(
            'sites', 'logs', 'cloudflare_deployments'
        )
    
    def affecting_production(self):
        """Get events affecting production sites."""
        return self.filter(sites__environment='production').distinct()
    
    def affecting_staging(self):
        """Get events affecting staging sites."""
        return self.filter(sites__environment='staging').distinct()
    
    def by_duration_range(self, min_minutes: Optional[int] = None, max_minutes: Optional[int] = None):
        """Filter by event duration."""
        queryset = self.filter(ended_at__isnull=False)
        
        if min_minutes is not None:
            min_duration = timedelta(minutes=min_minutes)
            queryset = queryset.extra(
                where=["ended_at - started_at >= %s"],
                params=[min_duration]
            )
        
        if max_minutes is not None:
            max_duration = timedelta(minutes=max_minutes)
            queryset = queryset.extra(
                where=["ended_at - started_at <= %s"],
                params=[max_duration]
            )
        
        return queryset


class MaintenanceEventManager(models.Manager):
    """Custom manager for MaintenanceEvent."""
    
    def get_queryset(self):
        return MaintenanceEventQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get events for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get events by status."""
        return self.get_queryset().by_status(status)
    
    def by_reason(self, reason: str):
        """Get events by reason."""
        return self.get_queryset().by_reason(reason)
    
    def active(self):
        """Get active events."""
        return self.get_queryset().active()
    
    def completed(self):
        """Get completed events."""
        return self.get_queryset().completed()
    
    def failed(self):
        """Get failed events."""
        return self.get_queryset().failed()
    
    def cancelled(self):
        """Get cancelled events."""
        return self.get_queryset().cancelled()
    
    def scheduled(self):
        """Get scheduled events."""
        return self.get_queryset().scheduled()
    
    def recent(self, days: int = 7):
        """Get recent events."""
        return self.get_queryset().recent(days)
    
    def long_running(self, hours: int = 2):
        """Get long-running events."""
        return self.get_queryset().long_running(hours)
    
    def with_sites(self):
        """Get events with sites."""
        return self.get_queryset().with_sites()
    
    def with_logs(self):
        """Get events with logs."""
        return self.get_queryset().with_logs()
    
    def with_deployments(self):
        """Get events with deployments."""
        return self.get_queryset().with_deployments()
    
    def with_full_relations(self):
        """Get events with all relations."""
        return self.get_queryset().with_full_relations()
    
    def affecting_production(self):
        """Get events affecting production."""
        return self.get_queryset().affecting_production()
    
    def affecting_staging(self):
        """Get events affecting staging."""
        return self.get_queryset().affecting_staging()
    
    def by_duration_range(self, min_minutes: Optional[int] = None, max_minutes: Optional[int] = None):
        """Get events by duration range."""
        return self.get_queryset().by_duration_range(min_minutes, max_minutes)
    
    def create_event(
        self,
        title: str,
        initiated_by,
        reason: str,
        site_ids: Optional[List[int]] = None,
        estimated_duration: Optional[timedelta] = None,
        maintenance_message: Optional[str] = None,
        **kwargs
    ):
        """Create a new maintenance event."""
        event = self.create(
            title=title,
            initiated_by=initiated_by,
            reason=reason,
            estimated_duration=estimated_duration,
            maintenance_message=maintenance_message or f"Maintenance in progress: {reason}",
            **kwargs
        )
        
        if site_ids:
            # Add sites to the event
            from ..models import CloudflareSite
            sites = CloudflareSite.objects.filter(id__in=site_ids)
            event.sites.add(*sites)
        
        return event
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get maintenance event statistics for user."""
        events = self.for_user(user)
        
        return {
            'total': events.count(),
            'active': events.active().count(),
            'completed': events.completed().count(),
            'failed': events.failed().count(),
            'cancelled': events.cancelled().count(),
            'scheduled': events.scheduled().count(),
            'recent': events.recent().count(),
            'long_running': events.long_running().count(),
            'affecting_production': events.affecting_production().count(),
            'avg_duration_minutes': self._get_avg_duration_minutes(events),
            'success_rate': self._get_success_rate(events),
        }
    
    def get_maintenance_calendar(self, user, days: int = 30) -> List[Dict[str, Any]]:
        """Get maintenance calendar for user."""
        cutoff = timezone.now() - timedelta(days=days)
        events = self.for_user(user).filter(
            created_at__gte=cutoff
        ).with_sites().order_by('created_at')
        
        calendar = []
        for event in events:
            calendar.append({
                'id': event.id,
                'title': event.title,
                'status': event.status,
                'reason': event.reason,
                'created_at': event.created_at,
                'started_at': event.started_at,
                'ended_at': event.ended_at,
                'duration': event.duration,
                'sites_count': event.sites.count(),
                'sites': [site.domain for site in event.sites.all()[:5]],  # Limit to 5
            })
        
        return calendar
    
    def _get_avg_duration_minutes(self, queryset) -> Optional[float]:
        """Calculate average duration in minutes."""
        completed = queryset.completed().filter(
            started_at__isnull=False,
            ended_at__isnull=False
        )
        
        if not completed.exists():
            return None
        
        total_seconds = 0
        count = 0
        
        for event in completed:
            if event.duration:
                total_seconds += event.duration.total_seconds()
                count += 1
        
        return (total_seconds / count / 60) if count > 0 else None
    
    def _get_success_rate(self, queryset) -> float:
        """Calculate success rate percentage."""
        total = queryset.filter(status__in=['completed', 'failed']).count()
        if total == 0:
            return 0.0
        
        successful = queryset.completed().count()
        return (successful / total) * 100


class MaintenanceLogQuerySet(models.QuerySet):
    """Custom queryset for MaintenanceLog."""
    
    def for_event(self, event):
        """Filter logs for specific maintenance event."""
        return self.filter(maintenance_event=event)
    
    def by_level(self, level: str):
        """Filter by log level."""
        return self.filter(level=level)
    
    def info(self):
        """Get info level logs."""
        return self.filter(level='info')
    
    def warning(self):
        """Get warning level logs."""
        return self.filter(level='warning')
    
    def error(self):
        """Get error level logs."""
        return self.filter(level='error')
    
    def recent(self, minutes: int = 60):
        """Get recent logs."""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return self.filter(timestamp__gte=cutoff)
    
    def with_event(self):
        """Include related maintenance event."""
        return self.select_related('maintenance_event')


class MaintenanceLogManager(models.Manager):
    """Custom manager for MaintenanceLog."""
    
    def get_queryset(self):
        return MaintenanceLogQuerySet(self.model, using=self._db)
    
    def for_event(self, event):
        """Get logs for specific event."""
        return self.get_queryset().for_event(event)
    
    def by_level(self, level: str):
        """Get logs by level."""
        return self.get_queryset().by_level(level)
    
    def info(self):
        """Get info logs."""
        return self.get_queryset().info()
    
    def warning(self):
        """Get warning logs."""
        return self.get_queryset().warning()
    
    def error(self):
        """Get error logs."""
        return self.get_queryset().error()
    
    def recent(self, minutes: int = 60):
        """Get recent logs."""
        return self.get_queryset().recent(minutes)
    
    def with_event(self):
        """Get logs with event."""
        return self.get_queryset().with_event()
    
    def log_info(self, event, message: str, **kwargs):
        """Create info log entry."""
        return self.create(
            maintenance_event=event,
            level='info',
            message=message,
            **kwargs
        )
    
    def log_warning(self, event, message: str, **kwargs):
        """Create warning log entry."""
        return self.create(
            maintenance_event=event,
            level='warning',
            message=message,
            **kwargs
        )
    
    def log_error(self, event, message: str, **kwargs):
        """Create error log entry."""
        return self.create(
            maintenance_event=event,
            level='error',
            message=message,
            **kwargs
        )
