"""
Maintenance Application Configuration

Follows django-cfg patterns for app configuration with automatic setup.
"""

from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MaintenanceConfig(AppConfig):
    """Maintenance application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.maintenance"
    label = "django_cfg_maintenance"
    verbose_name = "Django CFG Maintenance"

    def ready(self):
        """Initialize the maintenance application."""
        # Import signal handlers
        try:
            import django_cfg.apps.maintenance.signals  # noqa
        except ImportError:
            pass
        
        # Auto-setup Cloudflare if configured
        self._setup_cloudflare_auto_config()
    
    def _setup_cloudflare_auto_config(self):
        """Auto-setup Cloudflare configuration if API token and domain are provided."""
        try:
            # Check if basic Cloudflare config is available
            api_token = getattr(settings, 'CLOUDFLARE_API_TOKEN', None)
            domain = getattr(settings, 'CLOUDFLARE_DOMAIN', None)
            
            if api_token and domain:
                logger.info("Cloudflare maintenance mode auto-configuration detected")
                
                # Import here to avoid circular imports
                from django_cfg.apps.maintenance.services.auto_setup import CloudflareAutoSetup
                from django_cfg.models.cloudflare import CloudflareConfig
                
                # Create configuration
                config = CloudflareConfig(
                    api_token=api_token,
                    domain=domain
                )
                
                # Run auto-setup in background (non-blocking)
                import asyncio
                try:
                    # Try to get existing event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, schedule the task
                        asyncio.create_task(self._run_auto_setup(config))
                    else:
                        # If no loop is running, run in new thread
                        import threading
                        thread = threading.Thread(
                            target=self._run_auto_setup_sync,
                            args=(config,)
                        )
                        thread.daemon = True
                        thread.start()
                except RuntimeError:
                    # No event loop, run in thread
                    import threading
                    thread = threading.Thread(
                        target=self._run_auto_setup_sync,
                        args=(config,)
                    )
                    thread.daemon = True
                    thread.start()
                
        except Exception as e:
            logger.warning(f"Cloudflare auto-setup skipped: {e}")
    
    async def _run_auto_setup(self, config):
        """Run auto-setup asynchronously."""
        try:
            from django_cfg.apps.maintenance.services.auto_setup import CloudflareAutoSetup
            
            setup_service = CloudflareAutoSetup(config)
            result = await setup_service.setup_complete_infrastructure()
            
            if result.success:
                logger.info(f"✅ Cloudflare auto-setup completed in {result.get_duration_seconds():.2f}s")
            else:
                logger.warning(f"❌ Cloudflare auto-setup failed: {len(result.get_failed_steps())} errors")
                
        except Exception as e:
            logger.error(f"Cloudflare auto-setup error: {e}")
    
    def _run_auto_setup_sync(self, config):
        """Run auto-setup synchronously in thread."""
        try:
            import asyncio
            asyncio.run(self._run_auto_setup(config))
        except Exception as e:
            logger.error(f"Cloudflare auto-setup thread error: {e}")
