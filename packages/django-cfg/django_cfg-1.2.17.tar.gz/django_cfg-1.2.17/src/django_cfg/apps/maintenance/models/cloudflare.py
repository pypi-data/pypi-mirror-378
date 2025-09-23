"""
Cloudflare integration models.

Models for tracking Cloudflare deployments and configurations.
Following CRITICAL_REQUIREMENTS - proper typing, no raw Dict usage.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from datetime import timedelta
import json


class CloudflareDeployment(models.Model):
    """
    Cloudflare Worker deployment tracking.
    
    Tracks deployment of maintenance mode Workers to Cloudflare
    with full audit trail and rollback capabilities.
    """
    
    class Status(models.TextChoices):
        """Deployment status choices."""
        PENDING = "pending", "Pending"
        DEPLOYING = "deploying", "Deploying"
        DEPLOYED = "deployed", "Deployed"
        FAILED = "failed", "Failed"
        ROLLED_BACK = "rolled_back", "Rolled Back"
    
    class DeploymentType(models.TextChoices):
        """Type of deployment."""
        WORKER = "worker", "Cloudflare Worker"
        PAGE_RULE = "page_rule", "Page Rule"
        DNS_RECORD = "dns_record", "DNS Record"
        SSL_SETTING = "ssl_setting", "SSL Setting"
        CUSTOM_ERROR_PAGE = "custom_error_page", "Custom Error Page"
    
    # === Basic Information ===
    site = models.ForeignKey(
        'django_cfg_maintenance.CloudflareSite',
        on_delete=models.CASCADE,
        related_name='deployments',
        help_text="Site this deployment belongs to"
    )
    deployment_type = models.CharField(
        max_length=50,
        choices=DeploymentType.choices,
        default=DeploymentType.WORKER,
        help_text="Type of Cloudflare resource being deployed"
    )
    
    # === Deployment Details ===
    resource_name = models.CharField(
        max_length=200,
        help_text="Name of the deployed resource (Worker name, Page Rule, etc.)"
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cloudflare resource ID after deployment"
    )
    
    # === Status Tracking ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current deployment status"
    )
    
    # === Timing ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When deployment was initiated"
    )
    deployed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When deployment completed successfully"
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When deployment failed"
    )
    
    # === Configuration ===
    configuration = models.JSONField(
        default=dict,
        help_text="Deployment configuration (Worker script, Page Rule settings, etc.)"
    )
    
    # === Results ===
    cloudflare_response = models.JSONField(
        default=dict,
        blank=True,
        help_text="Full response from Cloudflare API"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if deployment failed"
    )
    
    # === Rollback Support ===
    previous_deployment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rollback_deployments',
        help_text="Previous deployment for rollback"
    )
    rollback_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data needed for rollback (previous configuration, etc.)"
    )
    
    # === Maintenance Event Link ===
    maintenance_event = models.ForeignKey(
        'django_cfg_maintenance.MaintenanceEvent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cloudflare_deployments',
        help_text="Related maintenance event"
    )
    
    # === Custom Manager ===
    from ..managers.deployments import CloudflareDeploymentManager
    objects = CloudflareDeploymentManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cloudflare Deployment"
        verbose_name_plural = "Cloudflare Deployments"
        indexes = [
            models.Index(fields=['site', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['deployment_type', '-created_at']),
            models.Index(fields=['resource_id']),
        ]
    
    def __str__(self) -> str:
        return f"{self.get_deployment_type_display()}: {self.resource_name} ({self.get_status_display()})"
    
    @property
    def is_active(self) -> bool:
        """Check if deployment is currently active."""
        return self.status == self.Status.DEPLOYED
    
    @property
    def is_pending(self) -> bool:
        """Check if deployment is pending."""
        return self.status in [self.Status.PENDING, self.Status.DEPLOYING]
    
    @property
    def deployment_duration(self) -> Optional[timedelta]:
        """Calculate deployment duration."""
        if self.deployed_at:
            return self.deployed_at - self.created_at
        elif self.failed_at:
            return self.failed_at - self.created_at
        elif self.status == self.Status.DEPLOYING:
            return timezone.now() - self.created_at
        return None
    
    @property
    def can_rollback(self) -> bool:
        """Check if deployment can be rolled back."""
        return (
            self.status == self.Status.DEPLOYED and
            (self.previous_deployment is not None or self.rollback_data)
        )
    
    def mark_deploying(self) -> None:
        """Mark deployment as in progress."""
        self.status = self.Status.DEPLOYING
        self.save(update_fields=['status'])
    
    def mark_deployed(self, resource_id: str, cloudflare_response: Dict[str, Any]) -> None:
        """Mark deployment as successful."""
        self.status = self.Status.DEPLOYED
        self.resource_id = resource_id
        self.deployed_at = timezone.now()
        self.cloudflare_response = cloudflare_response
        self.save(update_fields=[
            'status', 
            'resource_id', 
            'deployed_at', 
            'cloudflare_response'
        ])
    
    def mark_failed(self, error_message: str, cloudflare_response: Optional[Dict[str, Any]] = None) -> None:
        """Mark deployment as failed."""
        self.status = self.Status.FAILED
        self.failed_at = timezone.now()
        self.error_message = error_message
        if cloudflare_response:
            self.cloudflare_response = cloudflare_response
        
        self.save(update_fields=[
            'status', 
            'failed_at', 
            'error_message', 
            'cloudflare_response'
        ])
    
    def rollback(self) -> bool:
        """Attempt to rollback this deployment."""
        if not self.can_rollback:
            return False
        
        try:
            # Create rollback deployment record
            rollback_deployment = CloudflareDeployment.objects.create(
                site=self.site,
                deployment_type=self.deployment_type,
                resource_name=f"rollback-{self.resource_name}",
                configuration=self.rollback_data,
                previous_deployment=self,
                maintenance_event=self.maintenance_event
            )
            
            # Mark this deployment as rolled back
            self.status = self.Status.ROLLED_BACK
            self.save(update_fields=['status'])
            
            return True
            
        except Exception:
            return False
    
    def get_configuration_summary(self) -> str:
        """Get human-readable configuration summary."""
        if not self.configuration:
            return "No configuration"
        
        if self.deployment_type == self.DeploymentType.WORKER:
            return f"Worker script ({len(str(self.configuration.get('script', '')))} chars)"
        elif self.deployment_type == self.DeploymentType.PAGE_RULE:
            actions = self.configuration.get('actions', [])
            return f"Page Rule with {len(actions)} actions"
        elif self.deployment_type == self.DeploymentType.DNS_RECORD:
            record_type = self.configuration.get('type', 'Unknown')
            content = self.configuration.get('content', 'Unknown')
            return f"{record_type} record: {content}"
        else:
            return f"{len(self.configuration)} configuration items"
    
    def get_error_summary(self) -> str:
        """Get concise error summary."""
        if not self.error_message:
            return "No error"
        
        # Extract first line of error message
        first_line = self.error_message.split('\n')[0]
        return first_line[:200] if len(first_line) > 200 else first_line
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate resource name
        if not self.resource_name.strip():
            raise ValidationError({'resource_name': 'Resource name cannot be empty'})
        
        # Validate timing
        if self.deployed_at and self.failed_at:
            raise ValidationError("Deployment cannot be both successful and failed")
        
        if self.deployed_at and self.deployed_at < self.created_at:
            raise ValidationError({'deployed_at': 'Deployed time cannot be before created time'})
        
        if self.failed_at and self.failed_at < self.created_at:
            raise ValidationError({'failed_at': 'Failed time cannot be before created time'})
    
    @classmethod
    def create_worker_deployment(cls, 
                                site: 'CloudflareSite', 
                                worker_name: str, 
                                script_content: str,
                                maintenance_event: Optional['MaintenanceEvent'] = None) -> 'CloudflareDeployment':
        """Create Worker deployment record."""
        return cls.objects.create(
            site=site,
            deployment_type=cls.DeploymentType.WORKER,
            resource_name=worker_name,
            configuration={
                'script': script_content,
                'name': worker_name
            },
            maintenance_event=maintenance_event
        )
    
    @classmethod
    def create_page_rule_deployment(cls,
                                   site: 'CloudflareSite',
                                   rule_name: str,
                                   pattern: str,
                                   actions: Dict[str, Any],
                                   maintenance_event: Optional['MaintenanceEvent'] = None) -> 'CloudflareDeployment':
        """Create Page Rule deployment record."""
        return cls.objects.create(
            site=site,
            deployment_type=cls.DeploymentType.PAGE_RULE,
            resource_name=rule_name,
            configuration={
                'targets': [{'target': 'url', 'constraint': {'operator': 'matches', 'value': pattern}}],
                'actions': actions,
                'status': 'active'
            },
            maintenance_event=maintenance_event
        )
