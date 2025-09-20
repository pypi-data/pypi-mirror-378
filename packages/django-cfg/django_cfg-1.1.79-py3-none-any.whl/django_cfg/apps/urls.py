"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from django.urls import path, include
from typing import List
from django.urls import URLPattern


def get_django_cfg_urlpatterns() -> List[URLPattern]:
    """
    Get Django CFG URL patterns based on enabled applications.
    
    Returns:
        List of URL patterns for enabled django_cfg applications
    """
    from django_cfg.modules.base import BaseModule
    
    patterns = [
        # Core APIs (always enabled)
        path('health/', include('django_cfg.apps.api.health.urls')),
        path('commands/', include('django_cfg.apps.api.commands.urls')),
    ]
    
    try:
        # Use BaseModule to check enabled applications
        base_module = BaseModule()
        
        # Support URLs - needed for admin interface chat links
        # if base_module.is_support_enabled():
        #     patterns.append(path('support/', include('django_cfg.apps.support.urls')))
        # 
        # if base_module.is_accounts_enabled():
        #     patterns.append(path('accounts/', include('django_cfg.apps.accounts.urls')))
        
        # Newsletter and Leads are handled by Django Revolution zones
        # to avoid URL namespace conflicts and enable client generation
        # if base_module.is_newsletter_enabled():
        #     patterns.append(path('newsletter/', include('django_cfg.apps.newsletter.urls')))
        # 
        # if base_module.is_leads_enabled():
        #     patterns.append(path('leads/', include('django_cfg.apps.leads.urls')))
        
        # Tasks (Dramatiq) management URLs - Web interface for task management
        if base_module.is_tasks_enabled():
            patterns.append(path('tasks/', include('django_cfg.apps.tasks.urls')))
            
    except Exception:
        # Fallback: include all URLs if config is not available
        # Note: This fallback should not be needed in production
        pass
    
    return patterns


# Generate URL patterns dynamically
urlpatterns = get_django_cfg_urlpatterns()
