# Maintenance Services

Modern Cloudflare services using the official `cloudflare` Python library.

## Overview

This package provides clean, type-safe, and reliable integration with Cloudflare API v4 for maintenance mode management.

## Services

### CloudflareClient
Core client with rate limiting, retry logic, and error handling.

```python
from django_cfg.apps.maintenance.services import CloudflareClient
from django_cfg.models.cloudflare import CloudflareConfig

config = CloudflareConfig(api_token="your_token", domain="example.com")
client = CloudflareClient(config)

# List zones
zones = client.list_zones()

# Create DNS record
record = client.create_dns_record(
    zone_id="zone_id",
    record_type="A",
    name="api.example.com",
    content="1.2.3.4"
)
```

### SiteSyncService
Synchronizes Django CloudflareSite models with Cloudflare zones.

```python
from django_cfg.apps.maintenance.services import SiteSyncService

sync_service = SiteSyncService(config)

# Sync all sites for a user
stats = sync_service.sync_user_sites(
    user=user,
    dry_run=False,
    force_update=True
)
```

### MaintenanceManager
Manages maintenance mode using Cloudflare Workers.

```python
from django_cfg.apps.maintenance.services import MaintenanceManager

manager = MaintenanceManager(config)

# Enable maintenance mode
result = manager.enable_maintenance(
    site=site,
    maintenance_event=event,
    custom_message="We'll be back soon!"
)

# Disable maintenance mode
result = manager.disable_maintenance(site=site)
```

### WorkerManager
High-level Workers management.

```python
from django_cfg.apps.maintenance.services import WorkerManager

worker_manager = WorkerManager(config)

# Deploy a Worker
result = worker_manager.deploy_worker(
    account_id="account_id",
    script_name="my-worker",
    script_content=worker_code,
    routes=[{"zone_id": "zone_id", "pattern": "example.com/*"}]
)
```

### DNSManager
DNS operations with validation and bulk operations.

```python
from django_cfg.apps.maintenance.services import DNSManager

dns_manager = DNSManager(config)

# Create DNS record
result = dns_manager.create_dns_record(
    zone_id="zone_id",
    record_type="A",
    name="api.example.com",
    content="1.2.3.4"
)

# Bulk create records
result = dns_manager.bulk_create_records(
    zone_id="zone_id",
    records=[
        {"record_type": "A", "name": "api", "content": "1.2.3.4"},
        {"record_type": "CNAME", "name": "www", "content": "example.com"}
    ]
)
```

## Features

- **Official Library**: Uses the official `cloudflare` Python library
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Error Handling**: Comprehensive error handling with fallbacks
- **Type Safety**: Full type hints and validation
- **Bulk Operations**: Support for bulk DNS and Worker operations
- **Logging**: Detailed logging for debugging and monitoring
- **Django Integration**: Seamless integration with Django models

## Admin Integration

The services are integrated with Django Admin through Unfold actions:

- **Sync with Cloudflare**: Sync site DNS records
- **Validate Configuration**: Validate site configuration against Cloudflare
- **Bulk Operations**: Enable/disable maintenance for multiple sites

## Management Commands

```bash
# Sync sites with Cloudflare
python manage.py sync_cloudflare --user admin@example.com --api-token your_token

# Dry run
python manage.py sync_cloudflare --user admin@example.com --api-token your_token --dry-run
```

## Requirements

- `cloudflare>=3.0.0`
- Django 5.2+
- Python 3.10+

## Migration from Old Services

The old services in `services_old/` used manual HTTP requests. The new services provide:

1. **Better Error Handling**: Automatic retries and rate limiting
2. **Type Safety**: Full type hints and validation
3. **Official Support**: Uses the official Cloudflare library
4. **Modern Architecture**: Clean, maintainable code structure
5. **Better Testing**: Easier to mock and test

## Configuration

Services use `CloudflareConfig` from `django_cfg.models.cloudflare`:

```python
from django_cfg.models.cloudflare import CloudflareConfig

config = CloudflareConfig(
    api_token="your_cloudflare_api_token",
    domain="your_domain.com"
)
```

For production, store API tokens securely and implement proper token rotation.
