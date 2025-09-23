"""
Site synchronization service using official Cloudflare library.

Handles synchronization between Django CloudflareSite models and actual Cloudflare zones.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from .cloudflare_client import CloudflareClient
from ..models import CloudflareSite
from django_cfg.models.cloudflare import CloudflareConfig

User = get_user_model()
logger = logging.getLogger(__name__)


class SiteSyncService:
    """
    Service for synchronizing CloudflareSite models with Cloudflare zones.
    
    Provides bidirectional sync between Django models and Cloudflare API.
    """
    
    def __init__(self, config: CloudflareConfig):
        """Initialize sync service."""
        self.config = config
        self.client = CloudflareClient(config)
        
    def sync_user_sites(
        self,
        user: User,
        dry_run: bool = False,
        force_update: bool = False,
        environment: str = 'production',
        project: str = '',
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Sync all sites for a user with Cloudflare zones.
        
        Args:
            user: User to sync sites for
            dry_run: If True, only show what would be changed
            force_update: If True, update existing sites
            environment: Default environment for new sites
            project: Default project for new sites
            tags: Default tags for new sites
            
        Returns:
            Dict with sync statistics and results
        """
        logger.info(f"Starting site sync for user {user.username}")
        
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'sites': []
        }
        
        try:
            # Fetch zones from Cloudflare
            cf_zones = self.client.list_zones()
            logger.info(f"Found {len(cf_zones)} zones in Cloudflare")
            
            # Get existing sites for user
            existing_sites = {
                site.domain: site 
                for site in CloudflareSite.objects.for_user(user)
            }
            
            # Process each Cloudflare zone
            for zone in cf_zones:
                try:
                    result = self._sync_single_zone(
                        user=user,
                        zone=zone,
                        existing_sites=existing_sites,
                        dry_run=dry_run,
                        force_update=force_update,
                        environment=environment,
                        project=project,
                        tags=tags or []
                    )
                    
                    stats[result['action']] += 1
                    stats['sites'].append(result)
                    
                except Exception as e:
                    logger.error(f"Error syncing zone {zone.name}: {e}")
                    stats['errors'] += 1
                    stats['sites'].append({
                        'domain': zone.name,
                        'action': 'error',
                        'error': str(e)
                    })
            
            logger.info(f"Sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Site sync failed: {e}")
            raise
    
    def _sync_single_zone(
        self,
        user: User,
        zone: Any,  # Cloudflare Zone object
        existing_sites: Dict[str, CloudflareSite],
        dry_run: bool,
        force_update: bool,
        environment: str,
        project: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        """Sync a single Cloudflare zone with Django model."""
        domain = zone.name
        zone_id = zone.id
        
        existing_site = existing_sites.get(domain)
        
        if existing_site:
            if force_update:
                # Update existing site
                if not dry_run:
                    self._update_site_from_zone(existing_site, zone)
                
                return {
                    'domain': domain,
                    'action': 'updated',
                    'zone_id': zone_id,
                    'site_id': existing_site.id if existing_site else None
                }
            else:
                return {
                    'domain': domain,
                    'action': 'skipped',
                    'zone_id': zone_id,
                    'site_id': existing_site.id,
                    'reason': 'already_exists'
                }
        else:
            # Create new site
            if not dry_run:
                site = self._create_site_from_zone(
                    user=user,
                    zone=zone,
                    environment=environment,
                    project=project,
                    tags=tags
                )
                site_id = site.id
            else:
                site_id = None
            
            return {
                'domain': domain,
                'action': 'created',
                'zone_id': zone_id,
                'site_id': site_id
            }
    
    def _create_site_from_zone(
        self,
        user: User,
        zone: Any,
        environment: str,
        project: str,
        tags: List[str]
    ) -> CloudflareSite:
        """Create CloudflareSite from Cloudflare zone."""
        with transaction.atomic():
            # Get account ID
            account_id = getattr(zone.account, 'id', '') if hasattr(zone, 'account') else ''
            
            site = CloudflareSite.objects.create_site(
                name=zone.name,
                domain=zone.name,
                owner=user,
                environment=environment,
                project=project,
                tags=tags,
                # Cloudflare specific fields
                zone_id=zone.id,
                account_id=account_id,
                current_status=self._map_zone_status(zone.status),
                cloudflare_settings={
                    'zone_data': self._serialize_zone(zone),
                    'synced_at': timezone.now().isoformat(),
                    'sync_source': 'cloudflare_api'
                }
            )
            
            logger.info(f"Created site {site.name} from Cloudflare zone")
            return site
    
    def _update_site_from_zone(self, site: CloudflareSite, zone: Any) -> None:
        """Update CloudflareSite with data from Cloudflare zone."""
        with transaction.atomic():
            # Update zone-specific fields
            site.zone_id = zone.id
            site.current_status = self._map_zone_status(zone.status)
            
            # Update account ID if available
            if hasattr(zone, 'account') and zone.account:
                site.account_id = getattr(zone.account, 'id', site.account_id)
            
            # Update settings
            settings = site.cloudflare_settings or {}
            settings.update({
                'zone_data': self._serialize_zone(zone),
                'synced_at': timezone.now().isoformat(),
                'sync_source': 'cloudflare_api'
            })
            site.cloudflare_settings = settings
            
            site.save()
            logger.info(f"Updated site {site.name} from Cloudflare zone")
    
    def _map_zone_status(self, cf_status: str) -> str:
        """Map Cloudflare zone status to CloudflareSite status."""
        status_mapping = {
            'active': CloudflareSite.SiteStatus.ACTIVE,
            'pending': CloudflareSite.SiteStatus.UNKNOWN,
            'initializing': CloudflareSite.SiteStatus.UNKNOWN,
            'moved': CloudflareSite.SiteStatus.OFFLINE,
            'deleted': CloudflareSite.SiteStatus.OFFLINE,
            'deactivated': CloudflareSite.SiteStatus.OFFLINE,
        }
        return status_mapping.get(cf_status.lower(), CloudflareSite.SiteStatus.UNKNOWN)
    
    def _serialize_zone(self, zone: Any) -> Dict[str, Any]:
        """Serialize Cloudflare zone to standardized format."""
        # Use the client's serialize method if available
        if hasattr(self.client, 'serialize_zone'):
            return self.client.serialize_zone(zone)
        
        # Fallback to manual serialization
        try:
            if hasattr(zone, 'model_dump'):
                # Pydantic model
                return zone.model_dump()
            elif isinstance(zone, dict):
                # Already a dict
                return zone
            else:
                # Try to extract common attributes
                return {
                    'id': getattr(zone, 'id', ''),
                    'name': getattr(zone, 'name', ''),
                    'status': getattr(zone, 'status', 'unknown'),
                    'paused': getattr(zone, 'paused', False),
                    'type': getattr(zone, 'type', 'full'),
                    'development_mode': getattr(zone, 'development_mode', 0),
                    'name_servers': getattr(zone, 'name_servers', []),
                    'original_name_servers': getattr(zone, 'original_name_servers', []),
                    'original_registrar': getattr(zone, 'original_registrar', ''),
                    'original_dnshost': getattr(zone, 'original_dnshost', ''),
                    'created_on': getattr(zone, 'created_on', ''),
                    'modified_on': getattr(zone, 'modified_on', ''),
                    'activated_on': getattr(zone, 'activated_on', ''),
                    'account': getattr(zone, 'account', {})
                }
        except Exception as e:
            zone_name = getattr(zone, 'name', 'unknown')
            logger.warning(f"Failed to serialize zone {zone_name}: {e}")
            return {
                'id': getattr(zone, 'id', ''),
                'name': zone_name,
                'status': getattr(zone, 'status', 'unknown'),
                'error': f"Serialization failed: {e}"
            }
    
    def sync_site_dns_records(self, site: CloudflareSite) -> Dict[str, Any]:
        """
        Sync DNS records for a specific site.
        
        Args:
            site: CloudflareSite to sync DNS records for
            
        Returns:
            Dict with sync results
        """
        logger.info(f"Syncing DNS records for site {site.domain}")
        
        try:
            # Fetch DNS records from Cloudflare
            dns_records = self.client.list_dns_records(site.zone_id)
            
            # Update site settings with DNS records
            settings = site.cloudflare_settings or {}
            settings['dns_records'] = [
                {
                    'id': record.id,
                    'type': record.type,
                    'name': record.name,
                    'content': record.content,
                    'ttl': getattr(record, 'ttl', 300),
                    'proxied': getattr(record, 'proxied', False),
                    'created_on': getattr(record, 'created_on', ''),
                    'modified_on': getattr(record, 'modified_on', ''),
                }
                for record in dns_records
            ]
            settings['dns_synced_at'] = timezone.now().isoformat()
            
            site.cloudflare_settings = settings
            site.save()
            
            logger.info(f"Synced {len(dns_records)} DNS records for {site.domain}")
            
            return {
                'success': True,
                'records_count': len(dns_records),
                'synced_at': settings['dns_synced_at']
            }
            
        except Exception as e:
            logger.error(f"Failed to sync DNS records for {site.domain}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_site_configuration(self, site: CloudflareSite) -> Dict[str, Any]:
        """
        Validate site configuration against Cloudflare.
        
        Args:
            site: CloudflareSite to validate
            
        Returns:
            Dict with validation results
        """
        logger.info(f"Validating configuration for site {site.domain}")
        
        validation_results = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check if zone exists in Cloudflare
            cf_zone = self.client.get_zone(site.zone_id)
            if not cf_zone:
                validation_results['valid'] = False
                validation_results['issues'].append(
                    f"Zone {site.zone_id} not found in Cloudflare"
                )
                return validation_results
            
            # Check domain name consistency
            if cf_zone.name != site.domain:
                validation_results['warnings'].append(
                    f"Domain mismatch: Django={site.domain}, Cloudflare={cf_zone.name}"
                )
            
            # Check zone status
            if cf_zone.status != 'active':
                validation_results['warnings'].append(
                    f"Zone status is {cf_zone.status}, not active"
                )
            
            # Check if zone is paused
            if getattr(cf_zone, 'paused', False):
                validation_results['warnings'].append("Zone is paused in Cloudflare")
            
            logger.info(f"Validation completed for {site.domain}")
            
        except Exception as e:
            logger.error(f"Validation failed for {site.domain}: {e}")
            validation_results['valid'] = False
            validation_results['issues'].append(f"Validation error: {e}")
        
        return validation_results
    
    def get_sync_status(self, user: User) -> Dict[str, Any]:
        """
        Get synchronization status for user's sites.
        
        Args:
            user: User to get sync status for
            
        Returns:
            Dict with sync status information
        """
        sites = CloudflareSite.objects.for_user(user).with_full_relations()
        
        status = {
            'total_sites': sites.count(),
            'synced_sites': 0,
            'never_synced': 0,
            'outdated_sync': 0,
            'sync_errors': 0,
            'last_sync': None,
            'sites_status': []
        }
        
        now = timezone.now()
        sync_threshold = now - timezone.timedelta(hours=24)  # Consider outdated after 24h
        
        for site in sites:
            site_status = {
                'id': site.id,
                'domain': site.domain,
                'zone_id': site.zone_id,
                'status': 'unknown'
            }
            
            settings = site.cloudflare_settings or {}
            synced_at_str = settings.get('synced_at')
            
            if synced_at_str:
                try:
                    synced_at = datetime.fromisoformat(synced_at_str.replace('Z', '+00:00'))
                    synced_at = timezone.make_aware(synced_at) if timezone.is_naive(synced_at) else synced_at
                    
                    site_status['last_sync'] = synced_at.isoformat()
                    
                    if synced_at > sync_threshold:
                        site_status['status'] = 'synced'
                        status['synced_sites'] += 1
                    else:
                        site_status['status'] = 'outdated'
                        status['outdated_sync'] += 1
                    
                    # Update overall last sync
                    if not status['last_sync'] or synced_at.isoformat() > status['last_sync']:
                        status['last_sync'] = synced_at.isoformat()
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid sync timestamp for {site.domain}: {e}")
                    site_status['status'] = 'error'
                    status['sync_errors'] += 1
            else:
                site_status['status'] = 'never_synced'
                status['never_synced'] += 1
            
            status['sites_status'].append(site_status)
        
        return status
