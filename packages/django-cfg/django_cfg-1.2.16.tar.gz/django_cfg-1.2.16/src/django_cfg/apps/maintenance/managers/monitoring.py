"""
Custom managers for monitoring models.

Provides enhanced querying capabilities for MonitoringTarget model.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any
from datetime import timedelta


class MonitoringTargetQuerySet(models.QuerySet):
    """Custom queryset for MonitoringTarget."""
    
    def for_user(self, user):
        """Filter monitoring targets for sites owned by specific user."""
        return self.filter(site__owner=user)
    
    def active(self):
        """Get active monitoring targets."""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Get inactive monitoring targets."""
        return self.filter(is_active=False)
    
    def by_check_type(self, check_type: str):
        """Filter by check type."""
        return self.filter(check_type=check_type)
    
    def http_checks(self):
        """Get HTTP monitoring targets."""
        return self.filter(check_type='http')
    
    def tcp_checks(self):
        """Get TCP monitoring targets."""
        return self.filter(check_type='tcp')
    
    def ping_checks(self):
        """Get ping monitoring targets."""
        return self.filter(check_type='ping')
    
    def healthy(self):
        """Get targets with healthy status."""
        return self.filter(last_status='healthy')
    
    def unhealthy(self):
        """Get targets with unhealthy status."""
        return self.filter(last_status='unhealthy')
    
    def unknown_status(self):
        """Get targets with unknown status."""
        return self.filter(last_status='unknown')
    
    def recently_checked(self, minutes: int = 30):
        """Get targets checked recently."""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return self.filter(last_check__gte=cutoff)
    
    def overdue_check(self, multiplier: float = 2.0):
        """Get targets that are overdue for a check."""
        from django.db.models import F
        from django.utils import timezone
        
        # Calculate overdue threshold based on check_interval
        overdue_threshold = timezone.now() - timedelta(
            seconds=F('check_interval') * multiplier
        )
        
        return self.filter(
            is_active=True,
            last_check__lt=overdue_threshold
        )
    
    def with_failures(self, min_failures: int = 1):
        """Get targets with consecutive failures."""
        return self.filter(consecutive_failures__gte=min_failures)
    
    def high_failure_rate(self, min_percentage: float = 10.0):
        """Get targets with high failure rate."""
        from django.db.models import Case, When, F
        
        return self.annotate(
            failure_rate=Case(
                When(total_checks=0, then=0),
                default=F('total_failures') * 100.0 / F('total_checks')
            )
        ).filter(failure_rate__gte=min_percentage)
    
    def by_environment(self, environment: str):
        """Filter by site environment."""
        return self.filter(site__environment=environment)
    
    def production(self):
        """Get monitoring targets for production sites."""
        return self.filter(site__environment='production')
    
    def staging(self):
        """Get monitoring targets for staging sites."""
        return self.filter(site__environment='staging')
    
    def with_site(self):
        """Include related site in query."""
        return self.select_related('site')
    
    def with_site_owner(self):
        """Include site and owner in query."""
        return self.select_related('site__owner')


class MonitoringTargetManager(models.Manager):
    """Custom manager for MonitoringTarget."""
    
    def get_queryset(self):
        return MonitoringTargetQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get monitoring targets for specific user."""
        return self.get_queryset().for_user(user)
    
    def active(self):
        """Get active monitoring targets."""
        return self.get_queryset().active()
    
    def inactive(self):
        """Get inactive monitoring targets."""
        return self.get_queryset().inactive()
    
    def by_check_type(self, check_type: str):
        """Get targets by check type."""
        return self.get_queryset().by_check_type(check_type)
    
    def http_checks(self):
        """Get HTTP monitoring targets."""
        return self.get_queryset().http_checks()
    
    def tcp_checks(self):
        """Get TCP monitoring targets."""
        return self.get_queryset().tcp_checks()
    
    def ping_checks(self):
        """Get ping monitoring targets."""
        return self.get_queryset().ping_checks()
    
    def healthy(self):
        """Get healthy targets."""
        return self.get_queryset().healthy()
    
    def unhealthy(self):
        """Get unhealthy targets."""
        return self.get_queryset().unhealthy()
    
    def unknown_status(self):
        """Get targets with unknown status."""
        return self.get_queryset().unknown_status()
    
    def recently_checked(self, minutes: int = 30):
        """Get recently checked targets."""
        return self.get_queryset().recently_checked(minutes)
    
    def overdue_check(self, multiplier: float = 2.0):
        """Get overdue targets."""
        return self.get_queryset().overdue_check(multiplier)
    
    def with_failures(self, min_failures: int = 1):
        """Get targets with failures."""
        return self.get_queryset().with_failures(min_failures)
    
    def high_failure_rate(self, min_percentage: float = 10.0):
        """Get targets with high failure rate."""
        return self.get_queryset().high_failure_rate(min_percentage)
    
    def by_environment(self, environment: str):
        """Get targets by environment."""
        return self.get_queryset().by_environment(environment)
    
    def production(self):
        """Get production monitoring targets."""
        return self.get_queryset().production()
    
    def staging(self):
        """Get staging monitoring targets."""
        return self.get_queryset().staging()
    
    def with_site(self):
        """Get targets with site."""
        return self.get_queryset().with_site()
    
    def with_site_owner(self):
        """Get targets with site and owner."""
        return self.get_queryset().with_site_owner()
    
    def create_target(
        self,
        site,
        check_type: str = 'http',
        check_interval: int = 300,  # 5 minutes
        timeout: int = 30,
        retry_count: int = 3,
        expected_status_code: Optional[int] = None,
        expected_response_time: Optional[int] = None,
        custom_headers: Optional[Dict] = None,
        **kwargs
    ):
        """Create a new monitoring target."""
        return self.create(
            site=site,
            check_type=check_type,
            check_interval=check_interval,
            timeout=timeout,
            retry_count=retry_count,
            expected_status_code=expected_status_code or (200 if check_type == 'http' else None),
            expected_response_time=expected_response_time,
            custom_headers=custom_headers or {},
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get monitoring statistics for user."""
        targets = self.for_user(user)
        
        return {
            'total': targets.count(),
            'active': targets.active().count(),
            'inactive': targets.inactive().count(),
            'healthy': targets.healthy().count(),
            'unhealthy': targets.unhealthy().count(),
            'unknown': targets.unknown_status().count(),
            'http_checks': targets.http_checks().count(),
            'tcp_checks': targets.tcp_checks().count(),
            'ping_checks': targets.ping_checks().count(),
            'production': targets.production().count(),
            'staging': targets.staging().count(),
            'recently_checked': targets.recently_checked().count(),
            'overdue': targets.overdue_check().count(),
            'with_failures': targets.with_failures().count(),
            'high_failure_rate': targets.high_failure_rate().count(),
        }
    
    def get_health_summary(self, user) -> Dict[str, Any]:
        """Get health summary for user's monitoring targets."""
        targets = self.for_user(user).active()
        total = targets.count()
        
        if total == 0:
            return {
                'total_targets': 0,
                'health_percentage': 0,
                'unhealthy_count': 0,
                'overdue_count': 0,
                'critical_issues': [],
            }
        
        healthy = targets.healthy().count()
        unhealthy = targets.unhealthy().count()
        overdue = targets.overdue_check().count()
        
        # Get critical issues
        critical_issues = []
        
        # Production sites that are unhealthy
        prod_unhealthy = targets.production().unhealthy().with_site()
        for target in prod_unhealthy[:5]:  # Limit to 5
            critical_issues.append({
                'type': 'production_unhealthy',
                'site': target.site.domain,
                'last_check': target.last_check,
                'consecutive_failures': target.consecutive_failures,
            })
        
        # Sites with high failure rates
        high_failure = targets.high_failure_rate(20.0).with_site()
        for target in high_failure[:3]:  # Limit to 3
            failure_rate = (target.total_failures / target.total_checks * 100) if target.total_checks > 0 else 0
            critical_issues.append({
                'type': 'high_failure_rate',
                'site': target.site.domain,
                'failure_rate': round(failure_rate, 1),
                'total_failures': target.total_failures,
                'total_checks': target.total_checks,
            })
        
        return {
            'total_targets': total,
            'health_percentage': (healthy / total * 100) if total > 0 else 0,
            'unhealthy_count': unhealthy,
            'overdue_count': overdue,
            'critical_issues': critical_issues,
        }
    
    def get_targets_needing_check(self) -> 'MonitoringTargetQuerySet':
        """Get targets that need to be checked now."""
        now = timezone.now()
        
        return self.active().filter(
            models.Q(last_check__isnull=True) |
            models.Q(
                last_check__lt=now - timedelta(seconds=models.F('check_interval'))
            )
        )
