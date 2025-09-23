"""
Maintenance admin interfaces.

Rich Django admin interfaces for multi-site maintenance management.
Following django-cfg patterns with Unfold optimization.
"""

# Import all admin classes to register them
from .sites_admin import CloudflareSiteAdmin, SiteGroupAdmin
from .events_admin import MaintenanceEventAdmin, MaintenanceLogAdmin
from .monitoring_admin import MonitoringTargetAdmin
from .deployments_admin import CloudflareDeploymentAdmin

__all__ = [
    # Site management
    'CloudflareSiteAdmin',
    'SiteGroupAdmin',
    
    # Maintenance tracking
    'MaintenanceEventAdmin', 
    'MaintenanceLogAdmin',
    
    # Monitoring
    'MonitoringTargetAdmin',
    
    # Cloudflare integration
    'CloudflareDeploymentAdmin',
]
