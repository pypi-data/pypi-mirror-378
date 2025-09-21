"""
Django-CFG modules and utilities registry.
"""

MODULES_REGISTRY = {
    # URL integration
    "add_django_cfg_urls": ("django_cfg.core.integration", "add_django_cfg_urls"),
    "get_django_cfg_urls_info": ("django_cfg.core.integration", "get_django_cfg_urls_info"),
    
    # Configuration utilities
    "set_current_config": ("django_cfg.core.config", "set_current_config"),
}
