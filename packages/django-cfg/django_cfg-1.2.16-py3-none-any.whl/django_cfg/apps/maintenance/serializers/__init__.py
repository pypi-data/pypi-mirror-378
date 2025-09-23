"""
Maintenance app serializers.

Decomposed serializers for better organization and maintainability.
"""

from .base import UserSerializer, APIResponseSerializer
from .sites import (
    CloudflareSiteSerializer, CloudflareSiteCreateSerializer, CloudflareSiteListSerializer,
    SiteGroupSerializer, SiteGroupCreateSerializer
)
from .events import (
    MaintenanceEventSerializer, MaintenanceEventCreateSerializer, MaintenanceEventListSerializer,
    MaintenanceEventUpdateSerializer, MaintenanceLogSerializer
)
from .monitoring import (
    MonitoringTargetSerializer, MonitoringTargetCreateSerializer, HealthCheckResultSerializer
)
from .deployments import (
    CloudflareDeploymentSerializer, CloudflareDeploymentListSerializer
)
from .actions import (
    BulkMaintenanceActionSerializer, SiteFilterSerializer, SiteGroupActionSerializer,
    BulkOperationResultSerializer
)

__all__ = [
    # Base
    'UserSerializer',
    'APIResponseSerializer',
    'BulkOperationResultSerializer',
    
    # Sites
    'CloudflareSiteSerializer',
    'CloudflareSiteCreateSerializer',
    'CloudflareSiteListSerializer',
    'SiteGroupSerializer',
    'SiteGroupCreateSerializer',
    
    # Events
    'MaintenanceEventSerializer',
    'MaintenanceEventCreateSerializer',
    'MaintenanceEventListSerializer',
    'MaintenanceEventUpdateSerializer',
    'MaintenanceLogSerializer',
    
    # Monitoring
    'MonitoringTargetSerializer',
    'MonitoringTargetCreateSerializer',
    'HealthCheckResultSerializer',
    
    # Deployments
    'CloudflareDeploymentSerializer',
    'CloudflareDeploymentListSerializer',
    
    # Actions
    'BulkMaintenanceActionSerializer',
    'SiteFilterSerializer',
    'SiteGroupActionSerializer',
]
