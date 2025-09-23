"""
Cloudflare synchronization command service.

Handles the business logic for synchronizing sites with Cloudflare zones.
Extracted from management command for better testability and reusability.
"""

import logging
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from .site_sync import SiteSyncService
from ..models import CloudflareSite
from django_cfg.models.cloudflare import CloudflareConfig

User = get_user_model()
logger = logging.getLogger(__name__)


class SyncCommandService:
    """
    Service for handling Cloudflare synchronization command logic.
    
    Provides clean separation between command interface and business logic.
    """
    
    def __init__(self, config: CloudflareConfig):
        """Initialize sync command service."""
        self.config = config
        self.sync_service = SiteSyncService(config)
        
    def sync_user_sites_command(
        self,
        user: User,
        dry_run: bool = False,
        force_update: bool = False,
        environment: str = 'production',
        project: str = '',
        tags: List[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Execute site synchronization with command-specific logic.
        
        Args:
            user: User to sync sites for
            dry_run: If True, only show what would be changed
            force_update: If True, update existing sites
            environment: Default environment for new sites
            project: Default project for new sites
            tags: Default tags for new sites
            verbose: Enable verbose logging
            
        Returns:
            Dict with detailed sync results
        """
        logger.info(f"Starting command sync for user {user.username}")
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            # Use the core sync service
            core_stats = self.sync_service.sync_user_sites(
                user=user,
                dry_run=dry_run,
                force_update=force_update,
                environment=environment,
                project=project,
                tags=tags or []
            )
            
            # Transform results for command output
            command_stats = self._transform_stats_for_command(core_stats)
            
            logger.info(f"Command sync completed: {command_stats}")
            return {
                'success': True,
                'stats': command_stats,
                'core_stats': core_stats,
                'dry_run': dry_run
            }
            
        except Exception as e:
            logger.error(f"Command sync failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 1}
            }
    
    def get_user_by_identifier(self, user_identifier: str) -> User:
        """
        Get user by username or email.
        
        Args:
            user_identifier: Username or email address
            
        Returns:
            User instance
            
        Raises:
            User.DoesNotExist: If user not found
        """
        try:
            # Try by email first
            if '@' in user_identifier:
                return User.objects.get(email=user_identifier)
            else:
                return User.objects.get(username=user_identifier)
        except User.DoesNotExist:
            raise User.DoesNotExist(f"User not found: {user_identifier}")
    
    def get_api_token_for_user(self, user: User, provided_token: Optional[str] = None) -> str:
        """
        Get Cloudflare API token for user.
        
        Args:
            user: User to get token for
            provided_token: Explicitly provided token
            
        Returns:
            API token string
            
        Raises:
            ValueError: If no token available
        """
        if provided_token:
            return provided_token
        
        # Try to get from user's existing sites
        existing_site = CloudflareSite.objects.filter(owner=user).first()
        if existing_site and existing_site.api_token:
            return existing_site.api_token
        
        raise ValueError(
            "No API token available. Provide --api-token or ensure user has existing sites with tokens."
        )
    
    def validate_sync_parameters(
        self,
        user_identifier: str,
        api_token: Optional[str] = None,
        environment: str = 'production',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate synchronization parameters.
        
        Args:
            user_identifier: Username or email
            api_token: Cloudflare API token
            environment: Target environment
            **kwargs: Additional parameters
            
        Returns:
            Dict with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate user
        try:
            user = self.get_user_by_identifier(user_identifier)
            validation_result['user'] = user
        except User.DoesNotExist as e:
            validation_result['valid'] = False
            validation_result['errors'].append(str(e))
            return validation_result
        
        # Validate API token
        try:
            token = self.get_api_token_for_user(user, api_token)
            validation_result['api_token'] = token
        except ValueError as e:
            validation_result['valid'] = False
            validation_result['errors'].append(str(e))
        
        # Validate environment
        valid_environments = ['production', 'staging', 'development', 'testing']
        if environment not in valid_environments:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"Invalid environment '{environment}'. Must be one of: {valid_environments}"
            )
        
        # Check if user has existing sites
        existing_sites_count = CloudflareSite.objects.filter(owner=user).count()
        if existing_sites_count == 0:
            validation_result['warnings'].append(
                f"User {user.username} has no existing sites. All zones will be created as new sites."
            )
        else:
            validation_result['warnings'].append(
                f"User {user.username} has {existing_sites_count} existing sites."
            )
        
        return validation_result
    
    def get_sync_preview(
        self,
        user: User,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Get a preview of what would be synchronized without making changes.
        
        Args:
            user: User to preview sync for
            verbose: Include detailed information
            
        Returns:
            Dict with preview information
        """
        try:
            # Get current sync status
            sync_status = self.sync_service.get_sync_status(user)
            
            # Get zones from Cloudflare (this requires API call)
            cf_zones = self.sync_service.client.list_zones()
            
            # Get existing sites
            existing_sites = CloudflareSite.objects.for_user(user)
            existing_domains = set(existing_sites.values_list('domain', flat=True))
            
            # Analyze what would happen
            cf_domains = {zone.name for zone in cf_zones}
            
            preview = {
                'cloudflare_zones': len(cf_zones),
                'existing_sites': existing_sites.count(),
                'would_create': len(cf_domains - existing_domains),
                'would_update': len(cf_domains & existing_domains),
                'would_skip': len(existing_domains - cf_domains),
                'sync_status': sync_status
            }
            
            if verbose:
                preview.update({
                    'new_domains': list(cf_domains - existing_domains),
                    'existing_domains': list(cf_domains & existing_domains),
                    'orphaned_domains': list(existing_domains - cf_domains),
                    'cloudflare_zones_details': [
                        {
                            'name': zone.name,
                            'id': zone.id,
                            'status': zone.status
                        }
                        for zone in cf_zones
                    ]
                })
            
            return {
                'success': True,
                'preview': preview
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync preview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _transform_stats_for_command(self, core_stats: Dict[str, Any]) -> Dict[str, int]:
        """
        Transform core sync stats to command-compatible format.
        
        Args:
            core_stats: Stats from SiteSyncService
            
        Returns:
            Dict with command-compatible stats
        """
        # Map core stats to command stats
        command_stats = {
            'created': core_stats.get('created', 0),
            'updated': core_stats.get('updated', 0),
            'skipped': core_stats.get('skipped', 0),
            'errors': core_stats.get('errors', 0)
        }
        
        return command_stats
    
    def create_config_from_params(
        self,
        api_token: str,
        domain: str = "dummy.com"
    ) -> CloudflareConfig:
        """
        Create CloudflareConfig from parameters.
        
        Args:
            api_token: Cloudflare API token
            domain: Domain (not used for zone listing)
            
        Returns:
            CloudflareConfig instance
        """
        return CloudflareConfig(
            api_token=api_token,
            domain=domain
        )
    
    @classmethod
    def create_from_params(
        cls,
        api_token: str,
        domain: str = "dummy.com"
    ) -> 'SyncCommandService':
        """
        Create service instance from parameters.
        
        Args:
            api_token: Cloudflare API token
            domain: Domain (not used for zone listing)
            
        Returns:
            SyncCommandService instance
        """
        config = CloudflareConfig(
            api_token=api_token,
            domain=domain
        )
        return cls(config)
