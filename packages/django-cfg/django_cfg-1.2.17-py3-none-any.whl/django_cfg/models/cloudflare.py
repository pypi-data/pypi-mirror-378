"""
Cloudflare configuration models for django_cfg.

Type-safe Cloudflare maintenance mode configuration following CRITICAL_REQUIREMENTS.
No raw Dict/Any usage - everything through Pydantic v2 models.
"""

from typing import Annotated, Optional, List, Dict, Any
from pydantic import BaseModel, Field, SecretStr, field_validator, HttpUrl
from enum import Enum
from datetime import timedelta


class MaintenanceTemplate(str, Enum):
    """Available maintenance page templates."""
    BASIC = "basic"
    MODERN = "modern"
    CUSTOM = "custom"


class CloudflareConfig(BaseModel):
    """
    Zero-configuration Cloudflare maintenance mode setup.
    
    Following KISS principle - user provides only api_token and domain,
    everything else is auto-discovered and configured.
    """
    
    model_config = {
        "env_prefix": "CLOUDFLARE_",
        "case_sensitive": False,
        "validate_assignment": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
    
    # === Required Configuration (Zero-config approach) ===
    api_token: SecretStr = Field(
        description="Cloudflare API token with Zone:Edit permissions"
    )
    domain: Annotated[str, Field(
        min_length=3,
        max_length=253,
        pattern=r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
        description="Domain name (auto-discovers Zone ID)"
    )]
    
    # === Auto-discovered Fields (set by system) ===
    zone_id: Optional[str] = Field(
        default=None, 
        description="Auto-discovered Cloudflare Zone ID"
    )
    account_id: Optional[str] = Field(
        default=None, 
        description="Auto-discovered Cloudflare Account ID"
    )
    
    # === Optional Customization ===
    enabled: bool = Field(
        default=True,
        description="Enable Cloudflare maintenance mode integration"
    )
    
    template: MaintenanceTemplate = Field(
        default=MaintenanceTemplate.MODERN,
        description="Maintenance page template"
    )
    
    maintenance_title: str = Field(
        default="Site Under Maintenance",
        max_length=200,
        description="Title for maintenance page"
    )
    
    maintenance_message: str = Field(
        default="We're performing scheduled maintenance. Please try again shortly.",
        max_length=1000,
        description="Message for maintenance page"
    )
    
    # === Auto-configuration Flags ===
    auto_ssl: bool = Field(
        default=True, 
        description="Automatically configure SSL/TLS settings"
    )
    auto_dns: bool = Field(
        default=True, 
        description="Create missing DNS records automatically"
    )
    auto_monitoring: bool = Field(
        default=True, 
        description="Enable external monitoring"
    )
    
    # === Advanced Settings (Smart Defaults) ===
    worker_name: str = Field(
        default="maintenance-mode",
        max_length=100,
        pattern=r"^[a-zA-Z0-9\-_]+$",
        description="Cloudflare Worker name"
    )
    
    monitoring_interval: Annotated[int, Field(
        ge=30, 
        le=3600,
        description="Health check interval in seconds"
    )] = 60
    
    failure_threshold: Annotated[int, Field(
        ge=1, 
        le=10,
        description="Consecutive failures before enabling maintenance"
    )] = 3
    
    recovery_threshold: Annotated[int, Field(
        ge=1, 
        le=10,
        description="Consecutive successes before disabling maintenance"
    )] = 2
    
    # === Multi-site Support ===
    multi_site_enabled: bool = Field(
        default=False,
        description="Enable multi-site management features"
    )
    
    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain name."""
        domain = v.lower().strip()
        
        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            raise ValueError('Domain should not include protocol (http:// or https://)')
        
        # Remove www prefix for consistency
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Basic domain validation
        if not domain or '.' not in domain:
            raise ValueError('Domain must be a valid domain name')
        
        return domain
    
    def get_api_token(self) -> str:
        """Get decrypted API token."""
        return self.api_token.get_secret_value()
    
    def is_configured(self) -> bool:
        """Check if Cloudflare is fully configured."""
        return bool(self.zone_id and self.account_id)


class MultiSiteConfig(BaseModel):
    """
    Multi-site management configuration.
    
    Extends CloudflareConfig for managing multiple sites.
    """
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }
    
    # === Site Discovery ===
    auto_discover_sites: bool = Field(
        default=True,
        description="Automatically discover all sites in Cloudflare account"
    )
    
    site_filters: List[str] = Field(
        default_factory=list,
        description="Domain patterns to include (e.g., ['*.example.com', 'api.*.com'])"
    )
    
    excluded_domains: List[str] = Field(
        default_factory=list,
        description="Domains to exclude from management"
    )
    
    # === Default Site Settings ===
    default_environment: str = Field(
        default="production",
        pattern=r"^(production|staging|development|testing)$",
        description="Default environment for discovered sites"
    )
    
    default_project: str = Field(
        default="",
        max_length=100,
        description="Default project name for discovered sites"
    )
    
    default_tags: List[str] = Field(
        default_factory=list,
        description="Default tags for discovered sites"
    )
    
    # === Bulk Operations ===
    max_concurrent_operations: Annotated[int, Field(
        ge=1, 
        le=50,
        description="Maximum concurrent Cloudflare API operations"
    )] = 10
    
    operation_timeout: Annotated[int, Field(
        ge=5, 
        le=300,
        description="Timeout for individual operations in seconds"
    )] = 30
    
    # === Notifications ===
    notification_channels: List[str] = Field(
        default_factory=lambda: ["email"],
        description="Notification channels for maintenance events"
    )
    
    webhook_url: Optional[HttpUrl] = Field(
        default=None,
        description="Webhook URL for maintenance notifications"
    )


class MonitoringConfig(BaseModel):
    """
    External monitoring configuration.
    
    Configures health checks and automatic maintenance triggers.
    """
    
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }
    
    # === Monitoring Settings ===
    enabled: bool = Field(
        default=True,
        description="Enable external monitoring"
    )
    
    check_interval: Annotated[int, Field(
        ge=10, 
        le=3600,
        description="Health check interval in seconds"
    )] = 60
    
    timeout: Annotated[int, Field(
        ge=1, 
        le=300,
        description="Health check timeout in seconds"
    )] = 10
    
    # === Health Check Configuration ===
    health_check_path: str = Field(
        default="/health/",
        description="Health check endpoint path"
    )
    
    expected_status_codes: List[int] = Field(
        default_factory=lambda: [200, 201, 204],
        description="Expected HTTP status codes for healthy response"
    )
    
    expected_response_time_ms: Optional[int] = Field(
        default=5000,
        ge=100,
        le=60000,
        description="Maximum expected response time in milliseconds"
    )
    
    # === Failure Detection ===
    failure_threshold: Annotated[int, Field(
        ge=1, 
        le=20,
        description="Consecutive failures before triggering maintenance"
    )] = 3
    
    recovery_threshold: Annotated[int, Field(
        ge=1, 
        le=20,
        description="Consecutive successes before disabling maintenance"
    )] = 2
    
    # === Advanced Settings ===
    user_agent: str = Field(
        default="Django-CFG-Monitor/1.0",
        description="User agent for health checks"
    )
    
    follow_redirects: bool = Field(
        default=True,
        description="Follow HTTP redirects during health checks"
    )
    
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates during health checks"
    )
    
    custom_headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom headers for health check requests"
    )


# Export all models
__all__ = [
    "CloudflareConfig",
    "MultiSiteConfig", 
    "MonitoringConfig",
    "MaintenanceTemplate",
]
