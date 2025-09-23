"""
Multi-site management models.

Models for managing multiple Cloudflare sites with ORM-like interface.
Following CRITICAL_REQUIREMENTS - proper typing, no raw Dict usage.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, List, Dict, Any
from datetime import timedelta
import re

User = get_user_model()


class CloudflareSite(models.Model):
    """
    Individual Cloudflare site configuration.
    
    Represents a single site/domain managed through Cloudflare with
    maintenance mode capabilities and monitoring.
    """
    
    class SiteEnvironment(models.TextChoices):
        """Site environment types."""
        PRODUCTION = "production", "Production"
        STAGING = "staging", "Staging"
        DEVELOPMENT = "development", "Development"
        TESTING = "testing", "Testing"

    class SiteStatus(models.TextChoices):
        """Site operational status."""
        ACTIVE = "active", "Active"
        MAINTENANCE = "maintenance", "Under Maintenance"
        OFFLINE = "offline", "Offline"
        UNKNOWN = "unknown", "Unknown"
    
    # === Basic Information ===
    name = models.CharField(
        max_length=100,
        help_text="Friendly site name for identification"
    )
    domain = models.CharField(
        max_length=253,
        unique=True,
        help_text="Domain name (e.g., example.com)"
    )
    description = models.TextField(
        blank=True,
        help_text="Site description or notes"
    )
    
    # === Cloudflare Configuration ===
    zone_id = models.CharField(
        max_length=32,
        unique=True,
        help_text="Cloudflare Zone ID"
    )
    account_id = models.CharField(
        max_length=32,
        help_text="Cloudflare Account ID"
    )
    api_token = models.CharField(
        max_length=200,
        help_text="Site-specific or account API token"
    )
    
    # === Site Classification ===
    environment = models.CharField(
        max_length=20,
        choices=SiteEnvironment.choices,
        default=SiteEnvironment.PRODUCTION,
        help_text="Site environment type"
    )
    project = models.CharField(
        max_length=100,
        blank=True,
        help_text="Project or client name"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom tags for filtering and organization"
    )
    
    # === Current State ===
    current_status = models.CharField(
        max_length=20,
        choices=SiteStatus.choices,
        default=SiteStatus.UNKNOWN,
        help_text="Current operational status"
    )
    maintenance_active = models.BooleanField(
        default=False,
        help_text="Whether maintenance mode is currently active"
    )
    last_status_check = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When status was last checked"
    )
    
    # === Maintenance Configuration ===
    worker_name = models.CharField(
        max_length=100,
        default="maintenance-mode",
        help_text="Cloudflare Worker name for maintenance mode"
    )
    maintenance_template = models.CharField(
        max_length=50,
        default="modern",
        help_text="Maintenance page template"
    )
    custom_maintenance_message = models.TextField(
        blank=True,
        help_text="Custom maintenance message for this site"
    )
    
    # === Monitoring Settings ===
    monitoring_enabled = models.BooleanField(
        default=True,
        help_text="Enable health monitoring for this site"
    )
    health_check_url = models.URLField(
        blank=True,
        help_text="Custom health check URL (defaults to domain/health/)"
    )
    check_interval = models.PositiveIntegerField(
        default=300,  # 5 minutes
        help_text="Health check interval in seconds"
    )
    
    # === Access Control ===
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_sites',
        help_text="Site owner"
    )
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='accessible_sites',
        help_text="Users with access to manage this site"
    )
    
    # === Metadata ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_maintenance_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When maintenance was last activated"
    )
    
    # === Custom Manager ===
    from ..managers.sites import CloudflareSiteManager
    objects = CloudflareSiteManager()
    
    class Meta:
        ordering = ['name']
        verbose_name = "Cloudflare Site"
        verbose_name_plural = "Cloudflare Sites"
        indexes = [
            models.Index(fields=['owner', 'environment']),
            models.Index(fields=['project', 'environment']),
            models.Index(fields=['current_status']),
            models.Index(fields=['maintenance_active']),
            models.Index(fields=['domain']),
        ]
    
    def __str__(self) -> str:
        status_emoji = {
            self.SiteStatus.ACTIVE: "🟢",
            self.SiteStatus.MAINTENANCE: "🔧",
            self.SiteStatus.OFFLINE: "🔴",
            self.SiteStatus.UNKNOWN: "❓"
        }.get(self.current_status, "❓")
        
        return f"{status_emoji} {self.name} ({self.domain})"
    
    @property
    def is_production(self) -> bool:
        """Check if this is a production site."""
        return self.environment == self.SiteEnvironment.PRODUCTION
    
    @property
    def maintenance_duration(self) -> Optional[timedelta]:
        """Calculate current maintenance duration."""
        if self.maintenance_active and self.last_maintenance_at:
            return timezone.now() - self.last_maintenance_at
        return None
    
    @property
    def health_check_endpoint(self) -> str:
        """Get health check URL for this site."""
        if self.health_check_url:
            return self.health_check_url
        
        # Default health check endpoint
        protocol = "https" if self.is_production else "http"
        return f"{protocol}://{self.domain}/health/"
    
    def has_tag(self, tag: str) -> bool:
        """Check if site has specific tag."""
        return tag in (self.tags or [])
    
    def add_tag(self, tag: str) -> None:
        """Add tag to site."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags', 'updated_at'])
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from site."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags', 'updated_at'])
    
    def enable_maintenance(self, user: Optional[User] = None) -> None:
        """Enable maintenance mode for this site."""
        self.maintenance_active = True
        self.current_status = self.SiteStatus.MAINTENANCE
        self.last_maintenance_at = timezone.now()
        self.save(update_fields=[
            'maintenance_active', 
            'current_status', 
            'last_maintenance_at', 
            'updated_at'
        ])
    
    def disable_maintenance(self) -> None:
        """Disable maintenance mode for this site."""
        self.maintenance_active = False
        self.current_status = self.SiteStatus.ACTIVE
        self.save(update_fields=[
            'maintenance_active', 
            'current_status', 
            'updated_at'
        ])
    
    def update_status(self, status: str) -> None:
        """Update site status."""
        self.current_status = status
        self.last_status_check = timezone.now()
        self.save(update_fields=[
            'current_status', 
            'last_status_check', 
            'updated_at'
        ])
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate domain format
        domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
            r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        )
        if not domain_pattern.match(self.domain):
            raise ValidationError({'domain': 'Invalid domain format'})
        
        # Validate zone_id format (Cloudflare zone IDs are 32 chars)
        if len(self.zone_id) != 32:
            raise ValidationError({'zone_id': 'Zone ID must be 32 characters'})
        
        # Validate worker name
        worker_pattern = re.compile(r'^[a-zA-Z0-9\-_]+$')
        if not worker_pattern.match(self.worker_name):
            raise ValidationError({
                'worker_name': 'Worker name can only contain letters, numbers, hyphens, and underscores'
            })
        
        # Validate check interval
        if self.check_interval < 30:
            raise ValidationError({'check_interval': 'Check interval must be at least 30 seconds'})


class SiteGroup(models.Model):
    """
    Logical grouping of sites for bulk operations.
    
    Allows organizing sites by project, client, environment, or any other
    criteria for efficient bulk maintenance operations.
    """
    
    # === Basic Information ===
    name = models.CharField(
        max_length=100,
        help_text="Group name"
    )
    description = models.TextField(
        blank=True,
        help_text="Group description"
    )
    
    # === Relationships ===
    sites = models.ManyToManyField(
        CloudflareSite,
        related_name='groups',
        help_text="Sites in this group"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Group owner"
    )
    
    # === Group Settings ===
    auto_maintenance_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Automatic maintenance rules for this group"
    )
    notification_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Notification preferences for group events"
    )
    
    # === Metadata ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === Custom Manager ===
    from ..managers.sites import SiteGroupManager
    objects = SiteGroupManager()
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'owner']
        verbose_name = "Site Group"
        verbose_name_plural = "Site Groups"
        indexes = [
            models.Index(fields=['owner', 'name']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.sites.count()} sites)"
    
    @property
    def sites_count(self) -> int:
        """Count of sites in this group."""
        return self.sites.count()
    
    @property
    def active_sites_count(self) -> int:
        """Count of active sites in this group."""
        return self.sites.filter(current_status=CloudflareSite.SiteStatus.ACTIVE).count()
    
    @property
    def maintenance_sites_count(self) -> int:
        """Count of sites in maintenance in this group."""
        return self.sites.filter(maintenance_active=True).count()
    
    def get_sites_by_environment(self, environment: str) -> models.QuerySet:
        """Get sites in this group by environment."""
        return self.sites.filter(environment=environment)
    
    def get_sites_by_status(self, status: str) -> models.QuerySet:
        """Get sites in this group by status."""
        return self.sites.filter(current_status=status)
    
    def add_sites(self, sites: List[CloudflareSite]) -> None:
        """Add multiple sites to this group."""
        self.sites.add(*sites)
    
    def remove_sites(self, sites: List[CloudflareSite]) -> None:
        """Remove multiple sites from this group."""
        self.sites.remove(*sites)
    
    def enable_maintenance_for_all(self, user: Optional[User] = None) -> Dict[str, Any]:
        """Enable maintenance for all sites in group."""
        results = {
            'total': 0,
            'successful': [],
            'failed': []
        }
        
        for site in self.sites.all():
            results['total'] += 1
            try:
                site.enable_maintenance(user)
                results['successful'].append(site.domain)
            except Exception as e:
                results['failed'].append({
                    'site': site.domain,
                    'error': str(e)
                })
        
        return results
    
    def disable_maintenance_for_all(self) -> Dict[str, Any]:
        """Disable maintenance for all sites in group."""
        results = {
            'total': 0,
            'successful': [],
            'failed': []
        }
        
        for site in self.sites.filter(maintenance_active=True):
            results['total'] += 1
            try:
                site.disable_maintenance()
                results['successful'].append(site.domain)
            except Exception as e:
                results['failed'].append({
                    'site': site.domain,
                    'error': str(e)
                })
        
        return results
