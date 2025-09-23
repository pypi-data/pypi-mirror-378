# 🔧 Django-CFG Maintenance Application

**Multi-site maintenance mode management with Cloudflare integration**

## 🎯 Overview

The Django-CFG Maintenance application provides a comprehensive solution for managing maintenance mode across multiple Cloudflare sites with an ORM-like interface and zero-configuration setup.

### Key Features

- ✅ **Zero-Configuration Setup** - Just provide API token and domain
- ✅ **Multi-Site Management** - Manage hundreds of sites with ORM-like queries
- ✅ **Bulk Operations** - Enable/disable maintenance for multiple sites at once
- ✅ **External Monitoring** - Automatic maintenance triggers on health check failures
- ✅ **Rich Admin Interface** - Full Django admin integration with bulk actions
- ✅ **CLI Management** - Powerful management commands for automation
- ✅ **Audit Trail** - Complete logging and event tracking

## 🚀 Quick Start

### 1. Enable in Configuration

```python
# settings.py or your DjangoConfig
class MyProjectConfig(DjangoConfig):
    project_name = "My Project"
    enable_maintenance = True  # Enable maintenance app
    
    # Optional: Zero-config Cloudflare setup
    # Set these environment variables:
    # CLOUDFLARE_API_TOKEN=your_token
    # CLOUDFLARE_DOMAIN=example.com
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Basic Usage

#### ORM-like Interface

```python
from django_cfg.apps.maintenance.services import multi_site_manager

# Get sites for user
sites = multi_site_manager.sites(user)

# Enable maintenance for all production sites
await sites.production().enable_maintenance(
    reason="Database migration",
    message="We're upgrading our database. Back in 30 minutes!"
)

# Disable maintenance for specific project
await sites.filter(project='ecommerce').disable_maintenance()

# Complex filtering
critical_sites = sites.filter(
    environment='production',
    tags__contains='critical'
).exclude(project='legacy')

await critical_sites.enable_maintenance(reason="Security patch")
```

#### CLI Management

```bash
# Enable maintenance for all production sites
python manage.py maintenance enable --environment production --reason "Database upgrade"

# Disable maintenance for specific project
python manage.py maintenance disable --project myproject

# Check status of all sites
python manage.py maintenance status

# Discover new sites from Cloudflare
python manage.py maintenance discover --api-token your_token
```

#### Django Admin

- Navigate to `/admin/maintenance/`
- Use bulk actions to manage multiple sites
- View comprehensive dashboard with statistics
- Monitor maintenance events and logs

## 📊 Models

### CloudflareSite
Individual Cloudflare site configuration with maintenance capabilities.

### SiteGroup
Logical grouping of sites for bulk operations.

### MaintenanceEvent
Tracks maintenance events with full audit trail.

### MaintenanceLog
Detailed logging for maintenance operations.

### MonitoringTarget
External monitoring configuration for automatic triggers.

### CloudflareDeployment
Tracks Cloudflare Worker deployments with rollback support.

## 🔧 Services

### CloudflareService
Core Cloudflare API v4 integration with proper error handling and retries.

### CloudflareAutoSetup
Zero-configuration setup service that automatically discovers and configures Cloudflare resources.

### MultiSiteManager
ORM-like interface for multi-site management with bulk operations.

### MonitoringService
External health check monitoring with automatic maintenance triggers.

## 🎛️ Admin Interface

Rich Django admin interface with:

- **Site Dashboard** - Overview of all sites with statistics
- **Bulk Operations** - Enable/disable maintenance for multiple sites
- **Status Monitoring** - Real-time site status checks
- **Event Tracking** - Complete audit trail of maintenance events
- **Log Viewing** - Detailed operation logs with filtering

## 📱 Management Commands

### `maintenance`

Comprehensive CLI for maintenance management:

```bash
# Actions
python manage.py maintenance enable|disable|status|list|discover

# Filters
--domain example.com
--environment production|staging|development|testing
--project myproject
--tag critical
--owner username

# Options
--reason "Custom reason"
--message "Custom maintenance message"
--dry-run  # Preview without executing
--force    # Skip confirmation
--verbose  # Detailed output
```

## 🔍 Monitoring

### External Health Checks

The monitoring system performs external health checks and automatically triggers maintenance mode when sites become unavailable:

```python
# Configure monitoring target
target = MonitoringTarget.objects.create(
    site=site,
    check_url=f"https://{site.domain}/health/",
    check_interval=60,  # seconds
    failure_threshold=3,
    recovery_threshold=2,
    auto_enable_maintenance=True,
    auto_disable_maintenance=True
)
```

### Health Check Results

All health check results are stored with detailed information:
- Response time
- Status code
- Error messages
- Success/failure tracking

## 🌐 Zero-Configuration Setup

The auto-setup service automatically configures:

1. **Zone Discovery** - Finds Zone ID from domain name
2. **Account Discovery** - Extracts Account ID from zone data
3. **SSL Configuration** - Sets appropriate SSL/TLS mode
4. **DNS Records** - Creates missing DNS records if needed
5. **Worker Deployment** - Deploys maintenance mode Worker
6. **Monitoring Setup** - Configures health checks

```python
from django_cfg.models.cloudflare import CloudflareConfig
from django_cfg.apps.maintenance.services import CloudflareAutoSetup

config = CloudflareConfig(
    api_token="your_token",
    domain="example.com"
)

setup = CloudflareAutoSetup(config)
result = await setup.setup_complete_infrastructure()

if result.success:
    print(f"✅ Setup completed in {result.get_duration_seconds():.2f}s")
else:
    print(f"❌ Setup failed: {result.error_message}")
```

## 🔐 Security

- **API Token Security** - Tokens stored securely with proper field types
- **User Permissions** - Site-level access control with owner/shared model
- **Audit Trail** - Complete logging of all maintenance operations
- **Input Validation** - Comprehensive validation using Pydantic v2

## 📈 Scalability

- **Bulk Operations** - Handle hundreds of sites simultaneously
- **Async Processing** - Non-blocking operations with proper error handling
- **Rate Limiting** - Respects Cloudflare API rate limits
- **Retry Logic** - Exponential backoff for failed operations
- **Connection Pooling** - Efficient HTTP connection management

## 🧪 Testing

```bash
# Run maintenance app tests
python manage.py test django_cfg.apps.maintenance

# Test with coverage
coverage run --source='.' manage.py test django_cfg.apps.maintenance
coverage report
```

## 📚 API Reference

### Multi-Site Manager

```python
from django_cfg.apps.maintenance.services import multi_site_manager

# Get sites queryset
sites = multi_site_manager.sites(user)

# Filtering methods
sites.production()           # Production sites
sites.staging()             # Staging sites  
sites.active()              # Active sites
sites.in_maintenance()      # Sites in maintenance
sites.by_project('name')    # Filter by project
sites.with_tag('tag')       # Filter by tag

# Bulk operations
await sites.enable_maintenance(reason, message, user, dry_run)
await sites.disable_maintenance(user, dry_run)
await sites.check_status()

# Analysis
sites.get_environment_summary()  # Count by environment
sites.get_status_summary()       # Count by status
sites.get_project_summary()      # Count by project
```

### Cloudflare Service

```python
from django_cfg.apps.maintenance.services import CloudflareService

async with CloudflareService(api_token) as cf:
    # Zone management
    zones = await cf.get_zones()
    zone = await cf.get_zone_by_name('example.com')
    
    # Worker management
    result = await cf.deploy_worker(zone_id, worker_name, script_content)
    success = await cf.delete_worker(zone_id, worker_name)
    
    # DNS management
    record_id = await cf.create_dns_record(zone_id, 'A', 'www', '192.0.2.1')
    records = await cf.list_dns_records(zone_id)
    
    # SSL management
    settings = await cf.get_ssl_settings(zone_id)
    success = await cf.update_ssl_setting(zone_id, 'flexible')
```

## 🤝 Contributing

1. Follow CRITICAL_REQUIREMENTS.md for code standards
2. Use proper type hints and Pydantic models
3. Add comprehensive tests for new features
4. Update documentation for API changes
5. Follow django-cfg patterns and conventions

## 📄 License

Part of django-cfg package. See main package license.
