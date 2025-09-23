"""
URL configuration for maintenance app.

RESTful API endpoints using nested routers for multi-site maintenance management.
"""

from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    CloudflareSiteViewSet, SiteGroupViewSet, MaintenanceEventViewSet,
    MonitoringTargetViewSet, CloudflareDeploymentViewSet
)

app_name = 'maintenance'

# Main router for primary resources
router = routers.SimpleRouter()
router.register(r'sites', CloudflareSiteViewSet, basename='site')
router.register(r'groups', SiteGroupViewSet, basename='group')
router.register(r'events', MaintenanceEventViewSet, basename='event')
router.register(r'deployments', CloudflareDeploymentViewSet, basename='deployment')

# Nested routers for related resources
sites_router = routers.NestedSimpleRouter(router, r'sites', lookup='site')
sites_router.register(r'monitoring', MonitoringTargetViewSet, basename='site-monitoring')

events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
# events_router.register(r'logs', MaintenanceLogViewSet, basename='event-logs')  # Future

# API endpoints
urlpatterns = [
    # RESTful API routes
    path('api/', include(router.urls)),
    path('api/', include(sites_router.urls)),
    path('api/', include(events_router.urls)),
]
