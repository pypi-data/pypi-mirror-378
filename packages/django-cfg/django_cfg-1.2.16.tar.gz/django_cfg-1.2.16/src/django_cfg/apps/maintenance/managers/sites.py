"""
Custom managers for site-related models.

Provides enhanced querying capabilities for CloudflareSite and SiteGroup models.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any, List
from datetime import timedelta


class CloudflareSiteQuerySet(models.QuerySet):
    """Custom queryset for CloudflareSite."""
    
    def for_user(self, user):
        """Filter sites for specific user."""
        return self.filter(owner=user)
    
    def by_environment(self, environment: str):
        """Filter by site environment."""
        return self.filter(environment=environment)
    
    def by_status(self, status: str):
        """Filter by site status."""
        return self.filter(current_status=status)
    
    def by_project(self, project: str):
        """Filter by project name."""
        return self.filter(project__icontains=project)
    
    def by_domain(self, domain: str):
        """Filter by domain (exact or contains)."""
        return self.filter(domain__icontains=domain)
    
    def with_tags(self, tags: List[str]):
        """Filter sites that have any of the specified tags."""
        from django.contrib.postgres.fields import ArrayField
        from django.db.models import Q
        
        query = Q()
        for tag in tags:
            query |= Q(tags__contains=[tag])
        return self.filter(query)
    
    def production(self):
        """Get production sites."""
        return self.filter(environment='production')
    
    def staging(self):
        """Get staging sites."""
        return self.filter(environment='staging')
    
    def development(self):
        """Get development sites."""
        return self.filter(environment='development')
    
    def active(self):
        """Get active sites."""
        return self.filter(current_status='active')
    
    def in_maintenance(self):
        """Get sites currently in maintenance."""
        return self.filter(maintenance_active=True)
    
    def offline(self):
        """Get offline sites."""
        return self.filter(current_status='offline')
    
    def recent(self, days: int = 7):
        """Get recently created sites."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def recently_maintained(self, days: int = 7):
        """Get sites that had maintenance recently."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(last_maintenance_at__gte=cutoff)
    
    def with_monitoring(self):
        """Get sites that have monitoring configured."""
        return self.filter(monitoring_target__isnull=False)
    
    def without_monitoring(self):
        """Get sites without monitoring."""
        return self.filter(monitoring_target__isnull=True)
    
    def with_deployments(self):
        """Include related deployments in query."""
        return self.prefetch_related('deployments')
    
    def with_maintenance_events(self):
        """Include related maintenance events."""
        return self.prefetch_related('maintenance_events')
    
    def with_full_relations(self):
        """Include all related objects for detailed views."""
        return self.select_related('owner').prefetch_related(
            'deployments', 'maintenance_events', 'monitoring_target'
        )


class CloudflareSiteManager(models.Manager):
    """Custom manager for CloudflareSite."""
    
    def get_queryset(self):
        return CloudflareSiteQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get sites for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_environment(self, environment: str):
        """Get sites by environment."""
        return self.get_queryset().by_environment(environment)
    
    def by_status(self, status: str):
        """Get sites by status."""
        return self.get_queryset().by_status(status)
    
    def by_project(self, project: str):
        """Get sites by project."""
        return self.get_queryset().by_project(project)
    
    def by_domain(self, domain: str):
        """Get sites by domain."""
        return self.get_queryset().by_domain(domain)
    
    def with_tags(self, tags: List[str]):
        """Get sites with specific tags."""
        return self.get_queryset().with_tags(tags)
    
    def production(self):
        """Get production sites."""
        return self.get_queryset().production()
    
    def staging(self):
        """Get staging sites."""
        return self.get_queryset().staging()
    
    def development(self):
        """Get development sites."""
        return self.get_queryset().development()
    
    def active(self):
        """Get active sites."""
        return self.get_queryset().active()
    
    def in_maintenance(self):
        """Get sites in maintenance."""
        return self.get_queryset().in_maintenance()
    
    def offline(self):
        """Get offline sites."""
        return self.get_queryset().offline()
    
    def recent(self, days: int = 7):
        """Get recent sites."""
        return self.get_queryset().recent(days)
    
    def recently_maintained(self, days: int = 7):
        """Get recently maintained sites."""
        return self.get_queryset().recently_maintained(days)
    
    def with_monitoring(self):
        """Get sites with monitoring."""
        return self.get_queryset().with_monitoring()
    
    def without_monitoring(self):
        """Get sites without monitoring."""
        return self.get_queryset().without_monitoring()
    
    def with_deployments(self):
        """Get sites with deployments."""
        return self.get_queryset().with_deployments()
    
    def with_maintenance_events(self):
        """Get sites with maintenance events."""
        return self.get_queryset().with_maintenance_events()
    
    def with_full_relations(self):
        """Get sites with all relations."""
        return self.get_queryset().with_full_relations()
    
    def create_site(
        self,
        name: str,
        domain: str,
        owner,
        environment: str = 'production',
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        """Create a new Cloudflare site."""
        return self.create(
            name=name,
            domain=domain,
            owner=owner,
            environment=environment,
            project=project or '',
            tags=tags or [],
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get site statistics for user."""
        sites = self.for_user(user)
        
        return {
            'total': sites.count(),
            'production': sites.production().count(),
            'staging': sites.staging().count(),
            'development': sites.development().count(),
            'active': sites.active().count(),
            'in_maintenance': sites.in_maintenance().count(),
            'offline': sites.offline().count(),
            'with_monitoring': sites.with_monitoring().count(),
            'recent': sites.recent().count(),
            'recently_maintained': sites.recently_maintained().count(),
        }
    
    def get_maintenance_summary(self, user) -> Dict[str, Any]:
        """Get maintenance summary for user's sites."""
        sites = self.for_user(user)
        in_maintenance = sites.in_maintenance()
        
        return {
            'total_sites': sites.count(),
            'in_maintenance': in_maintenance.count(),
            'maintenance_percentage': (
                (in_maintenance.count() / sites.count() * 100) 
                if sites.count() > 0 else 0
            ),
            'production_in_maintenance': in_maintenance.production().count(),
            'staging_in_maintenance': in_maintenance.staging().count(),
            'recently_maintained': sites.recently_maintained().count(),
        }


class SiteGroupQuerySet(models.QuerySet):
    """Custom queryset for SiteGroup."""
    
    def for_user(self, user):
        """Filter groups for specific user."""
        return self.filter(owner=user)
    
    def by_environment(self, environment: str):
        """Filter groups by primary environment of their sites."""
        return self.filter(sites__environment=environment).distinct()
    
    def with_sites(self):
        """Include related sites in query."""
        return self.prefetch_related('sites')
    
    def with_active_sites(self):
        """Include only active sites."""
        return self.prefetch_related(
            models.Prefetch(
                'sites',
                queryset=CloudflareSiteQuerySet(self.model._meta.get_field('sites').related_model).active()
            )
        )
    
    def recent(self, days: int = 7):
        """Get recently created groups."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class SiteGroupManager(models.Manager):
    """Custom manager for SiteGroup."""
    
    def get_queryset(self):
        return SiteGroupQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get groups for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_environment(self, environment: str):
        """Get groups by environment."""
        return self.get_queryset().by_environment(environment)
    
    def with_sites(self):
        """Get groups with sites."""
        return self.get_queryset().with_sites()
    
    def with_active_sites(self):
        """Get groups with active sites."""
        return self.get_queryset().with_active_sites()
    
    def recent(self, days: int = 7):
        """Get recent groups."""
        return self.get_queryset().recent(days)
    
    def create_group(
        self,
        name: str,
        owner,
        description: Optional[str] = None,
        site_ids: Optional[List[int]] = None,
        **kwargs
    ):
        """Create a new site group."""
        group = self.create(
            name=name,
            owner=owner,
            description=description or '',
            **kwargs
        )
        
        if site_ids:
            # Add sites to the group
            from ..models import CloudflareSite
            sites = CloudflareSite.objects.filter(id__in=site_ids, owner=owner)
            group.sites.add(*sites)
        
        return group
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get group statistics for user."""
        groups = self.for_user(user)
        
        return {
            'total': groups.count(),
            'recent': groups.recent().count(),
            'total_sites_in_groups': sum(
                group.sites.count() for group in groups.with_sites()
            ),
            'avg_sites_per_group': (
                sum(group.sites.count() for group in groups.with_sites()) / groups.count()
                if groups.count() > 0 else 0
            ),
        }
