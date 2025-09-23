"""
Django-CFG Maintenance Application

Multi-site maintenance mode management with Cloudflare integration.
Provides zero-configuration setup and ORM-like interface for managing
maintenance mode across multiple sites.

Key Features:
- Zero-configuration Cloudflare setup
- Multi-site management with ORM-like queries
- External monitoring for automatic maintenance mode
- Rich Django admin interface
- Scheduled maintenance support
- Full audit trail and logging

Example Usage:
    # Zero-config setup
    CLOUDFLARE_API_TOKEN = "your_token"
    CLOUDFLARE_DOMAIN = "example.com"
    
    # Multi-site management
    sites = multi_site_manager.sites(user)
    await sites.production().enable_maintenance()
    await sites.filter(project='client-a').disable_maintenance()
"""

default_app_config = 'django_cfg.apps.maintenance.apps.MaintenanceConfig'
