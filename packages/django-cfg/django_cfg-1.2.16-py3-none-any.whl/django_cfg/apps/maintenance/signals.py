"""
Maintenance app signals.

Signal handlers for maintenance events and site management.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import logging

from .models import MaintenanceEvent, CloudflareSite

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MaintenanceEvent)
def maintenance_event_created(sender, instance, created, **kwargs):
    """Handle maintenance event creation."""
    if created:
        logger.info(f"Maintenance event created: {instance.title}")


@receiver(post_save, sender=CloudflareSite)
def cloudflare_site_updated(sender, instance, created, **kwargs):
    """Handle Cloudflare site updates."""
    if created:
        logger.info(f"New Cloudflare site added: {instance.domain}")
    else:
        logger.debug(f"Cloudflare site updated: {instance.domain}")


@receiver(pre_delete, sender=CloudflareSite)
def cloudflare_site_cleanup(sender, instance, **kwargs):
    """Clean up before deleting Cloudflare site."""
    logger.info(f"Cleaning up Cloudflare site: {instance.domain}")
    
    # Note: In a full implementation, this would clean up
    # any active Workers or Page Rules in Cloudflare
