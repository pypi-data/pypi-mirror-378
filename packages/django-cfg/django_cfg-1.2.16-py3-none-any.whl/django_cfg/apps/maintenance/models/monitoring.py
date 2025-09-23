"""
Monitoring models for external health checks.

Models for tracking health checks and automatic maintenance triggers.
Following CRITICAL_REQUIREMENTS - proper typing, no raw Dict usage.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from datetime import timedelta
import json


class MonitoringTarget(models.Model):
    """
    External monitoring target configuration.
    
    Defines what to monitor and how to trigger maintenance mode
    when health checks fail.
    """
    
    class Status(models.TextChoices):
        """Monitoring status choices."""
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        DISABLED = "disabled", "Disabled"
        ERROR = "error", "Error"
    
    # === Target Configuration ===
    site = models.OneToOneField(
        'django_cfg_maintenance.CloudflareSite',
        on_delete=models.CASCADE,
        related_name='monitoring_target',
        help_text="Site being monitored"
    )
    
    # === Health Check Settings ===
    check_url = models.URLField(
        help_text="URL to check for health status"
    )
    check_interval = models.PositiveIntegerField(
        default=60,
        help_text="Check interval in seconds"
    )
    timeout = models.PositiveIntegerField(
        default=10,
        help_text="Request timeout in seconds"
    )
    
    # === Expected Response ===
    expected_status_codes = models.JSONField(
        default=list,
        help_text="Expected HTTP status codes (e.g., [200, 201])"
    )
    expected_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum expected response time in milliseconds"
    )
    expected_content = models.TextField(
        blank=True,
        help_text="Expected content in response body (substring match)"
    )
    
    # === Failure Detection ===
    failure_threshold = models.PositiveIntegerField(
        default=3,
        help_text="Consecutive failures before triggering maintenance"
    )
    recovery_threshold = models.PositiveIntegerField(
        default=2,
        help_text="Consecutive successes before disabling maintenance"
    )
    
    # === Current State ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Current monitoring status"
    )
    consecutive_failures = models.PositiveIntegerField(
        default=0,
        help_text="Current consecutive failure count"
    )
    consecutive_successes = models.PositiveIntegerField(
        default=0,
        help_text="Current consecutive success count"
    )
    
    # === Last Check Results ===
    last_check_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last health check was performed"
    )
    last_check_success = models.BooleanField(
        default=True,
        help_text="Whether last check was successful"
    )
    last_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Response time of last check in milliseconds"
    )
    
    # === Maintenance Triggers ===
    auto_enable_maintenance = models.BooleanField(
        default=True,
        help_text="Automatically enable maintenance on failure threshold"
    )
    auto_disable_maintenance = models.BooleanField(
        default=True,
        help_text="Automatically disable maintenance on recovery threshold"
    )
    maintenance_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When maintenance was last auto-triggered"
    )
    
    # === Advanced Settings ===
    user_agent = models.CharField(
        max_length=200,
        default="Django-CFG-Monitor/1.0",
        help_text="User agent for health checks"
    )
    follow_redirects = models.BooleanField(
        default=True,
        help_text="Follow HTTP redirects during checks"
    )
    verify_ssl = models.BooleanField(
        default=True,
        help_text="Verify SSL certificates"
    )
    custom_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom headers for health check requests"
    )
    
    # === Metadata ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === Custom Manager ===
    from ..managers.monitoring import MonitoringTargetManager
    objects = MonitoringTargetManager()
    
    class Meta:
        verbose_name = "Monitoring Target"
        verbose_name_plural = "Monitoring Targets"
        indexes = [
            models.Index(fields=['status', 'last_check_at']),
            models.Index(fields=['site', '-last_check_at']),
        ]
    
    def __str__(self) -> str:
        return f"Monitor: {self.site.name} ({self.get_status_display()})"
    
    @property
    def is_healthy(self) -> bool:
        """Check if target is currently healthy."""
        return self.last_check_success and self.consecutive_failures == 0
    
    @property
    def should_trigger_maintenance(self) -> bool:
        """Check if maintenance should be triggered."""
        return (
            self.auto_enable_maintenance and
            self.consecutive_failures >= self.failure_threshold and
            not self.site.maintenance_active
        )
    
    @property
    def should_disable_maintenance(self) -> bool:
        """Check if maintenance should be disabled."""
        return (
            self.auto_disable_maintenance and
            self.consecutive_successes >= self.recovery_threshold and
            self.site.maintenance_active
        )
    
    @property
    def next_check_at(self) -> Optional[timezone.datetime]:
        """Calculate when next check should occur."""
        if self.last_check_at:
            return self.last_check_at + timedelta(seconds=self.check_interval)
        return timezone.now()
    
    def record_success(self, response_time_ms: int) -> None:
        """Record successful health check."""
        self.last_check_at = timezone.now()
        self.last_check_success = True
        self.last_response_time_ms = response_time_ms
        self.consecutive_failures = 0
        self.consecutive_successes += 1
        
        self.save(update_fields=[
            'last_check_at',
            'last_check_success', 
            'last_response_time_ms',
            'consecutive_failures',
            'consecutive_successes',
            'updated_at'
        ])
    
    def record_failure(self, error_message: str = "") -> None:
        """Record failed health check."""
        self.last_check_at = timezone.now()
        self.last_check_success = False
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        
        self.save(update_fields=[
            'last_check_at',
            'last_check_success',
            'consecutive_successes', 
            'consecutive_failures',
            'updated_at'
        ])
        
        # Create health check result record
        HealthCheckResult.objects.create(
            target=self,
            success=False,
            error_message=error_message
        )
    
    def trigger_maintenance(self) -> bool:
        """Trigger maintenance mode for this target."""
        if self.should_trigger_maintenance:
            self.site.enable_maintenance()
            self.maintenance_triggered_at = timezone.now()
            self.save(update_fields=['maintenance_triggered_at', 'updated_at'])
            return True
        return False
    
    def disable_maintenance_if_recovered(self) -> bool:
        """Disable maintenance if recovery threshold is met."""
        if self.should_disable_maintenance:
            self.site.disable_maintenance()
            return True
        return False
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate thresholds
        if self.failure_threshold < 1:
            raise ValidationError({'failure_threshold': 'Must be at least 1'})
        
        if self.recovery_threshold < 1:
            raise ValidationError({'recovery_threshold': 'Must be at least 1'})
        
        # Validate intervals
        if self.check_interval < 10:
            raise ValidationError({'check_interval': 'Must be at least 10 seconds'})
        
        if self.timeout >= self.check_interval:
            raise ValidationError({'timeout': 'Timeout must be less than check interval'})
        
        # Validate expected status codes
        if self.expected_status_codes:
            for code in self.expected_status_codes:
                if not isinstance(code, int) or code < 100 or code > 599:
                    raise ValidationError({
                        'expected_status_codes': 'Must contain valid HTTP status codes (100-599)'
                    })


class HealthCheckResult(models.Model):
    """
    Individual health check result record.
    
    Stores detailed results of each health check for analysis and debugging.
    """
    
    # === Relationships ===
    target = models.ForeignKey(
        MonitoringTarget,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Monitoring target this result belongs to"
    )
    
    # === Check Results ===
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the check was performed"
    )
    success = models.BooleanField(
        help_text="Whether the check was successful"
    )
    
    # === Response Details ===
    status_code = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="HTTP response status code"
    )
    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Response time in milliseconds"
    )
    response_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Response size in bytes"
    )
    
    # === Error Information ===
    error_message = models.TextField(
        blank=True,
        help_text="Error message if check failed"
    )
    error_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of error (timeout, connection, etc.)"
    )
    
    # === Additional Data ===
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional check details (headers, content, etc.)"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Health Check Result"
        verbose_name_plural = "Health Check Results"
        indexes = [
            models.Index(fields=['target', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self) -> str:
        status = "✅ Success" if self.success else "❌ Failed"
        return f"{status}: {self.target.site.name} at {self.timestamp}"
    
    @property
    def is_slow_response(self) -> bool:
        """Check if response was slower than expected."""
        if not self.response_time_ms or not self.target.expected_response_time_ms:
            return False
        return self.response_time_ms > self.target.expected_response_time_ms
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get response time in seconds."""
        if self.response_time_ms is not None:
            return self.response_time_ms / 1000.0
        return None
    
    def get_error_summary(self) -> str:
        """Get concise error summary."""
        if self.success:
            return "Success"
        
        if self.error_type and self.error_message:
            return f"{self.error_type}: {self.error_message[:100]}"
        elif self.error_message:
            return self.error_message[:100]
        elif self.status_code:
            return f"HTTP {self.status_code}"
        else:
            return "Unknown error"
    
    @classmethod
    def create_success(cls, target: MonitoringTarget, **kwargs) -> 'HealthCheckResult':
        """Create successful health check result."""
        return cls.objects.create(
            target=target,
            success=True,
            **kwargs
        )
    
    @classmethod
    def create_failure(cls, target: MonitoringTarget, error_message: str, **kwargs) -> 'HealthCheckResult':
        """Create failed health check result."""
        return cls.objects.create(
            target=target,
            success=False,
            error_message=error_message,
            **kwargs
        )
