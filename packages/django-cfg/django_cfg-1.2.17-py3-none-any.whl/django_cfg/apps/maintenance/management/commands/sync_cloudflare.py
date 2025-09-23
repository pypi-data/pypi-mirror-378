"""
Django management command for synchronizing sites with Cloudflare.

Fetches zones from Cloudflare API and creates/updates CloudflareSite records.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from typing import Dict, List, Any, Optional
import logging

from ...models import CloudflareSite
from ...services import SyncCommandService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize sites with Cloudflare zones."""
    
    help = 'Synchronize CloudflareSite records with Cloudflare zones'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--user',
            type=str,
            help='Username or email of the site owner (required)',
            required=True
        )
        
        parser.add_argument(
            '--api-token',
            type=str,
            help='Cloudflare API token (if not provided, will try to get from user config)',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synchronized without making changes',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing sites (overwrite local changes)',
        )
        
        parser.add_argument(
            '--environment',
            type=str,
            choices=['production', 'staging', 'development', 'testing'],
            default='production',
            help='Default environment for new sites (default: production)',
        )
        
        parser.add_argument(
            '--project',
            type=str,
            help='Default project name for new sites',
        )
        
        parser.add_argument(
            '--tags',
            type=str,
            nargs='*',
            help='Default tags for new sites (space-separated)',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Validate parameters
            validation = self._validate_parameters(options)
            if not validation['valid']:
                for error in validation['errors']:
                    self.stdout.write(self.style.ERROR(f"❌ {error}"))
                raise CommandError("Invalid parameters")
            
            # Show warnings
            for warning in validation['warnings']:
                self.stdout.write(self.style.WARNING(f"⚠️  {warning}"))
            
            # Initialize service
            sync_service = SyncCommandService.create_from_params(
                api_token=validation['api_token']
            )
            
            # Perform sync
            self.stdout.write("🔍 Syncing sites with Cloudflare...")
            result = sync_service.sync_user_sites_command(
                user=validation['user'],
                dry_run=options['dry_run'],
                force_update=options['force'],
                environment=options['environment'],
                project=options.get('project') or '',
                tags=options.get('tags') or [],
                verbose=options['verbose']
            )
            
            if result['success']:
                # Display results
                self._display_results(result['stats'], options['dry_run'])
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sync failed: {result['error']}"))
                raise CommandError(result['error'])
            
        except Exception as e:
            logger.exception("Command failed")
            raise CommandError(f"Synchronization failed: {e}")
    
    def _validate_parameters(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command parameters using service."""
        # Create temporary service for validation
        temp_service = SyncCommandService.create_from_params("dummy_token")
        
        return temp_service.validate_sync_parameters(
            user_identifier=options['user'],
            api_token=options.get('api_token'),
            environment=options['environment']
        )
    
    # Old methods removed - logic moved to SyncCommandService
    
    def _display_results(self, stats: Dict[str, int], dry_run: bool) -> None:
        """Display synchronization results."""
        mode = "DRY RUN" if dry_run else "COMPLETED"
        
        self.stdout.write(f"\n🎯 Synchronization {mode}")
        self.stdout.write("=" * 40)
        
        if stats['created'] > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✨ Created: {stats['created']} sites")
            )
        
        if stats['updated'] > 0:
            self.stdout.write(
                self.style.SUCCESS(f"🔄 Updated: {stats['updated']} sites")
            )
        
        if stats['skipped'] > 0:
            self.stdout.write(
                self.style.WARNING(f"⏭️  Skipped: {stats['skipped']} sites")
            )
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f"❌ Errors: {stats['errors']} sites")
            )
        
        total = sum(stats.values())
        self.stdout.write(f"\n📊 Total processed: {total} zones")
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE("\n💡 Run without --dry-run to apply changes")
            )
