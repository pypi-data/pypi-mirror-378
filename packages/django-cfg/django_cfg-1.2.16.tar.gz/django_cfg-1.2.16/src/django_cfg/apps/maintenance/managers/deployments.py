"""
Custom managers for deployment models.

Provides enhanced querying capabilities for CloudflareDeployment model.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any
from datetime import timedelta


class CloudflareDeploymentQuerySet(models.QuerySet):
    """Custom queryset for CloudflareDeployment."""
    
    def for_user(self, user):
        """Filter deployments for sites owned by specific user."""
        return self.filter(site__owner=user)
    
    def by_status(self, status: str):
        """Filter by deployment status."""
        return self.filter(status=status)
    
    def by_type(self, deployment_type: str):
        """Filter by deployment type."""
        return self.filter(deployment_type=deployment_type)
    
    def active(self):
        """Get active deployments."""
        return self.filter(status='active')
    
    def failed(self):
        """Get failed deployments."""
        return self.filter(status='failed')
    
    def rolled_back(self):
        """Get rolled back deployments."""
        return self.filter(status='rolled_back')
    
    def pending(self):
        """Get pending deployments."""
        return self.filter(status='pending')
    
    def worker_deployments(self):
        """Get Worker deployments."""
        return self.filter(deployment_type='worker')
    
    def page_rule_deployments(self):
        """Get Page Rule deployments."""
        return self.filter(deployment_type='page_rule')
    
    def custom_page_deployments(self):
        """Get Custom Page deployments."""
        return self.filter(deployment_type='custom_page')
    
    def dns_deployments(self):
        """Get DNS deployments."""
        return self.filter(deployment_type='dns')
    
    def recent(self, days: int = 7):
        """Get recent deployments."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(deployed_at__gte=cutoff)
    
    def successful(self):
        """Get successful deployments (active status)."""
        return self.filter(status='active')
    
    def by_environment(self, environment: str):
        """Filter by site environment."""
        return self.filter(site__environment=environment)
    
    def production(self):
        """Get deployments for production sites."""
        return self.filter(site__environment='production')
    
    def staging(self):
        """Get deployments for staging sites."""
        return self.filter(site__environment='staging')
    
    def for_maintenance_event(self, event):
        """Get deployments for specific maintenance event."""
        return self.filter(maintenance_event=event)
    
    def can_rollback(self):
        """Get deployments that can be rolled back."""
        return self.filter(
            status='active',
            deployment_type__in=['worker', 'page_rule']
        )
    
    def with_site(self):
        """Include related site in query."""
        return self.select_related('site')
    
    def with_maintenance_event(self):
        """Include related maintenance event."""
        return self.select_related('maintenance_event')
    
    def with_full_relations(self):
        """Include all related objects."""
        return self.select_related('site', 'maintenance_event')


class CloudflareDeploymentManager(models.Manager):
    """Custom manager for CloudflareDeployment."""
    
    def get_queryset(self):
        return CloudflareDeploymentQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get deployments for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get deployments by status."""
        return self.get_queryset().by_status(status)
    
    def by_type(self, deployment_type: str):
        """Get deployments by type."""
        return self.get_queryset().by_type(deployment_type)
    
    def active(self):
        """Get active deployments."""
        return self.get_queryset().active()
    
    def failed(self):
        """Get failed deployments."""
        return self.get_queryset().failed()
    
    def rolled_back(self):
        """Get rolled back deployments."""
        return self.get_queryset().rolled_back()
    
    def pending(self):
        """Get pending deployments."""
        return self.get_queryset().pending()
    
    def worker_deployments(self):
        """Get Worker deployments."""
        return self.get_queryset().worker_deployments()
    
    def page_rule_deployments(self):
        """Get Page Rule deployments."""
        return self.get_queryset().page_rule_deployments()
    
    def custom_page_deployments(self):
        """Get Custom Page deployments."""
        return self.get_queryset().custom_page_deployments()
    
    def dns_deployments(self):
        """Get DNS deployments."""
        return self.get_queryset().dns_deployments()
    
    def recent(self, days: int = 7):
        """Get recent deployments."""
        return self.get_queryset().recent(days)
    
    def successful(self):
        """Get successful deployments."""
        return self.get_queryset().successful()
    
    def by_environment(self, environment: str):
        """Get deployments by environment."""
        return self.get_queryset().by_environment(environment)
    
    def production(self):
        """Get production deployments."""
        return self.get_queryset().production()
    
    def staging(self):
        """Get staging deployments."""
        return self.get_queryset().staging()
    
    def for_maintenance_event(self, event):
        """Get deployments for maintenance event."""
        return self.get_queryset().for_maintenance_event(event)
    
    def can_rollback(self):
        """Get deployments that can be rolled back."""
        return self.get_queryset().can_rollback()
    
    def with_site(self):
        """Get deployments with site."""
        return self.get_queryset().with_site()
    
    def with_maintenance_event(self):
        """Get deployments with maintenance event."""
        return self.get_queryset().with_maintenance_event()
    
    def with_full_relations(self):
        """Get deployments with all relations."""
        return self.get_queryset().with_full_relations()
    
    def create_deployment(
        self,
        site,
        deployment_type: str,
        cloudflare_id: str,
        config: Optional[Dict] = None,
        maintenance_event=None,
        **kwargs
    ):
        """Create a new Cloudflare deployment."""
        return self.create(
            site=site,
            deployment_type=deployment_type,
            cloudflare_id=cloudflare_id,
            config=config or {},
            maintenance_event=maintenance_event,
            deployed_at=timezone.now(),
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get deployment statistics for user."""
        deployments = self.for_user(user)
        
        return {
            'total': deployments.count(),
            'active': deployments.active().count(),
            'failed': deployments.failed().count(),
            'rolled_back': deployments.rolled_back().count(),
            'pending': deployments.pending().count(),
            'worker_deployments': deployments.worker_deployments().count(),
            'page_rule_deployments': deployments.page_rule_deployments().count(),
            'custom_page_deployments': deployments.custom_page_deployments().count(),
            'dns_deployments': deployments.dns_deployments().count(),
            'production': deployments.production().count(),
            'staging': deployments.staging().count(),
            'recent': deployments.recent().count(),
            'can_rollback': deployments.can_rollback().count(),
            'success_rate': self._get_success_rate(deployments),
        }
    
    def get_deployment_summary(self, user) -> Dict[str, Any]:
        """Get deployment summary for user."""
        deployments = self.for_user(user)
        total = deployments.count()
        
        if total == 0:
            return {
                'total_deployments': 0,
                'success_rate': 0,
                'active_count': 0,
                'failed_count': 0,
                'recent_activity': [],
            }
        
        active = deployments.active().count()
        failed = deployments.failed().count()
        success_rate = self._get_success_rate(deployments)
        
        # Get recent activity
        recent_activity = []
        recent_deployments = deployments.recent(7).with_site().order_by('-deployed_at')[:10]
        
        for deployment in recent_deployments:
            recent_activity.append({
                'id': deployment.id,
                'site': deployment.site.domain,
                'type': deployment.deployment_type,
                'status': deployment.status,
                'deployed_at': deployment.deployed_at,
                'can_rollback': deployment.can_rollback,
            })
        
        return {
            'total_deployments': total,
            'success_rate': success_rate,
            'active_count': active,
            'failed_count': failed,
            'recent_activity': recent_activity,
        }
    
    def get_rollback_candidates(self, user) -> 'CloudflareDeploymentQuerySet':
        """Get deployments that can be rolled back for user."""
        return self.for_user(user).can_rollback().with_site().order_by('-deployed_at')
    
    def _get_success_rate(self, queryset) -> float:
        """Calculate success rate percentage."""
        total = queryset.count()
        if total == 0:
            return 0.0
        
        successful = queryset.successful().count()
        return (successful / total) * 100
