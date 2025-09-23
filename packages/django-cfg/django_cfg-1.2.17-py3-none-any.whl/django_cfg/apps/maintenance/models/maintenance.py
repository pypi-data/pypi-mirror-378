"""
Maintenance event models.

Core models for tracking maintenance events and logs.
Following CRITICAL_REQUIREMENTS - no raw Dict usage, proper typing.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Optional
from datetime import timedelta

User = get_user_model()


class MaintenanceEvent(models.Model):
    """
    Main maintenance event tracking model.
    
    Tracks maintenance events with full audit trail and Cloudflare integration.
    """
    
    class Status(models.TextChoices):
        """Maintenance event status choices."""
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
    
    class Reason(models.TextChoices):
        """Maintenance reason choices."""
        MANUAL = "manual", "Manual Activation"
        SERVER_DOWN = "server_down", "Server Unreachable"
        HIGH_ERROR_RATE = "high_error_rate", "High Error Rate"
        DATABASE_ISSUES = "database_issues", "Database Issues"
        DEPLOYMENT = "deployment", "Deployment"
        SECURITY_UPDATE = "security_update", "Security Update"
        SCHEDULED = "scheduled", "Scheduled Maintenance"
        EMERGENCY = "emergency", "Emergency Maintenance"
    
    # === Basic Information ===
    title = models.CharField(
        max_length=200,
        help_text="Human-readable maintenance event title"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of maintenance work"
    )
    reason = models.CharField(
        max_length=50,
        choices=Reason.choices,
        default=Reason.MANUAL,
        help_text="Reason for maintenance activation"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Current maintenance status"
    )
    
    # === Timing ===
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="When maintenance was started"
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When maintenance was completed"
    )
    estimated_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Estimated maintenance duration"
    )
    
    # === User Tracking ===
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_maintenance_events',
        help_text="User who initiated maintenance"
    )
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_maintenance_events',
        help_text="User who completed maintenance"
    )
    
    # === Cloudflare Integration ===
    cloudflare_worker_deployed = models.BooleanField(
        default=False,
        help_text="Whether Cloudflare Worker was deployed"
    )
    cloudflare_deployment_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cloudflare deployment identifier"
    )
    worker_deployment_success = models.BooleanField(
        default=False,
        help_text="Whether Worker deployment was successful"
    )
    
    # === Metrics ===
    affected_requests = models.PositiveIntegerField(
        default=0,
        help_text="Number of requests affected during maintenance"
    )
    error_count_before = models.PositiveIntegerField(
        default=0,
        help_text="Error count before maintenance"
    )
    error_count_during = models.PositiveIntegerField(
        default=0,
        help_text="Error count during maintenance"
    )
    
    # === Sites (Many-to-Many relationship) ===
    sites = models.ManyToManyField(
        'django_cfg_maintenance.CloudflareSite',
        blank=True,
        related_name='maintenance_events',
        help_text="Sites affected by this maintenance event"
    )
    
    # === Metadata ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === Custom Manager ===
    from ..managers.events import MaintenanceEventManager
    objects = MaintenanceEventManager()
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Maintenance Event"
        verbose_name_plural = "Maintenance Events"
        indexes = [
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['reason', '-started_at']),
            models.Index(fields=['initiated_by', '-started_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate actual maintenance duration."""
        if self.ended_at:
            return self.ended_at - self.started_at
        elif self.status == self.Status.ACTIVE:
            return timezone.now() - self.started_at
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if maintenance is currently active."""
        return self.status == self.Status.ACTIVE
    
    @property
    def is_scheduled(self) -> bool:
        """Check if maintenance is scheduled for future."""
        return self.status == self.Status.SCHEDULED
    
    @property
    def affected_sites_count(self) -> int:
        """Count of affected sites."""
        return self.sites.count()
    
    def complete(self, user: Optional[User] = None) -> None:
        """Mark maintenance as completed."""
        self.status = self.Status.COMPLETED
        self.ended_at = timezone.now()
        self.completed_by = user
        self.save(update_fields=['status', 'ended_at', 'completed_by', 'updated_at'])
    
    def cancel(self, user: Optional[User] = None) -> None:
        """Cancel maintenance event."""
        self.status = self.Status.CANCELLED
        self.ended_at = timezone.now()
        self.completed_by = user
        self.save(update_fields=['status', 'ended_at', 'completed_by', 'updated_at'])
    
    def fail(self, error_message: str = "") -> None:
        """Mark maintenance as failed."""
        self.status = self.Status.FAILED
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at', 'updated_at'])
        
        # Create failure log
        MaintenanceLog.objects.create(
            event=self,
            level=MaintenanceLog.Level.ERROR,
            message=f"Maintenance failed: {error_message}",
            details={'error': error_message}
        )
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate timing
        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError("End time cannot be before start time")
        
        # Validate estimated duration
        if self.estimated_duration and self.estimated_duration.total_seconds() <= 0:
            raise ValidationError("Estimated duration must be positive")


class MaintenanceLog(models.Model):
    """
    Detailed logging for maintenance events.
    
    Provides audit trail and debugging information for maintenance operations.
    """
    
    class Level(models.TextChoices):
        """Log level choices."""
        DEBUG = "debug", "Debug"
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        CRITICAL = "critical", "Critical"
    
    # === Relationships ===
    event = models.ForeignKey(
        MaintenanceEvent,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Related maintenance event"
    )
    
    # === Log Data ===
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.INFO,
        help_text="Log level"
    )
    message = models.TextField(
        help_text="Log message"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional log details (JSON)"
    )
    
    # === Context ===
    component = models.CharField(
        max_length=100,
        blank=True,
        help_text="Component that generated the log (e.g., 'cloudflare', 'monitoring')"
    )
    operation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Operation being performed (e.g., 'deploy_worker', 'health_check')"
    )
    
    # === User Context ===
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User associated with this log entry"
    )
    
    # === Metadata ===
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the log entry was created"
    )
    
    # === Custom Manager ===
    from ..managers.events import MaintenanceLogManager
    objects = MaintenanceLogManager()
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Maintenance Log"
        verbose_name_plural = "Maintenance Logs"
        indexes = [
            models.Index(fields=['event', '-timestamp']),
            models.Index(fields=['level', '-timestamp']),
            models.Index(fields=['component', '-timestamp']),
        ]
    
    def __str__(self) -> str:
        return f"{self.get_level_display()}: {self.message[:100]}"
    
    @classmethod
    def log_info(cls, event: MaintenanceEvent, message: str, **kwargs) -> 'MaintenanceLog':
        """Create info log entry."""
        return cls.objects.create(
            event=event,
            level=cls.Level.INFO,
            message=message,
            **kwargs
        )
    
    @classmethod
    def log_error(cls, event: MaintenanceEvent, message: str, **kwargs) -> 'MaintenanceLog':
        """Create error log entry."""
        return cls.objects.create(
            event=event,
            level=cls.Level.ERROR,
            message=message,
            **kwargs
        )
    
    @classmethod
    def log_warning(cls, event: MaintenanceEvent, message: str, **kwargs) -> 'MaintenanceLog':
        """Create warning log entry."""
        return cls.objects.create(
            event=event,
            level=cls.Level.WARNING,
            message=message,
            **kwargs
        )
