"""
Multi-site maintenance management command.

Provides CLI interface for managing maintenance mode across multiple sites
with ORM-like syntax and bulk operations.
"""

import asyncio
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import List, Optional

from django_cfg.apps.maintenance.services import MaintenanceManager
from django_cfg.apps.maintenance.models import CloudflareSite

User = get_user_model()


class Command(BaseCommand):
    """
    Multi-site maintenance management command.
    
    Examples:
        # Enable maintenance for all production sites
        python manage.py maintenance enable --environment production
        
        # Disable maintenance for specific project
        python manage.py maintenance disable --project myproject
        
        # Check status of all sites
        python manage.py maintenance status
        
        # Enable maintenance with custom message
        python manage.py maintenance enable --domain example.com --message "Upgrading database"
        
        # Bulk operations with filters
        python manage.py maintenance enable --tag critical --reason "Security patch"
    """
    
    help = 'Manage maintenance mode for multiple Cloudflare sites'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        # Main action
        parser.add_argument(
            'action',
            choices=['enable', 'disable', 'status', 'list', 'discover'],
            help='Action to perform'
        )
        
        # Site filters
        parser.add_argument(
            '--domain',
            help='Specific domain to target'
        )
        parser.add_argument(
            '--environment',
            choices=['production', 'staging', 'development', 'testing'],
            help='Filter by environment'
        )
        parser.add_argument(
            '--project',
            help='Filter by project name'
        )
        parser.add_argument(
            '--tag',
            help='Filter by tag'
        )
        parser.add_argument(
            '--owner',
            help='Filter by owner username'
        )
        
        # Maintenance options
        parser.add_argument(
            '--reason',
            default='Manual maintenance via CLI',
            help='Reason for maintenance'
        )
        parser.add_argument(
            '--message',
            help='Custom maintenance message'
        )
        
        # Operation options
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operation without confirmation'
        )
        
        # Discovery options
        parser.add_argument(
            '--api-token',
            help='Cloudflare API token for site discovery'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'csv'],
            default='table',
            help='Output format'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        self.options = options
        self.verbosity = options.get('verbosity', 1)
        
        try:
            # Get user for operations
            user = self._get_user(options.get('owner'))
            
            # Execute action
            if options['action'] == 'enable':
                asyncio.run(self._handle_enable(user))
            elif options['action'] == 'disable':
                asyncio.run(self._handle_disable(user))
            elif options['action'] == 'status':
                asyncio.run(self._handle_status(user))
            elif options['action'] == 'list':
                self._handle_list(user)
            elif options['action'] == 'discover':
                asyncio.run(self._handle_discover(user))
            
        except Exception as e:
            raise CommandError(f"Command failed: {str(e)}")
    
    def _get_user(self, username: Optional[str] = None) -> User:
        """Get user for operations."""
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found")
        else:
            # Use first superuser if no user specified
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                raise CommandError("No superuser found. Please specify --owner or create a superuser.")
            return superuser
    
    def _get_sites_queryset(self, user: User):
        """Get filtered sites queryset based on command options."""
        sites = multi_site_manager.sites(user)
        
        # Apply filters
        if self.options.get('domain'):
            sites = sites.filter(domain=self.options['domain'])
        
        if self.options.get('environment'):
            sites = sites.filter(environment=self.options['environment'])
        
        if self.options.get('project'):
            sites = sites.filter(project=self.options['project'])
        
        if self.options.get('tag'):
            sites = sites.with_tag(self.options['tag'])
        
        return sites
    
    async def _handle_enable(self, user: User):
        """Handle enable maintenance action."""
        sites = self._get_sites_queryset(user)
        
        if sites.count() == 0:
            self.stdout.write(self.style.WARNING("No sites match the specified filters."))
            return
        
        # Show what will be affected
        self.stdout.write(f"Will enable maintenance for {sites.count()} sites:")
        for site in sites.all()[:10]:  # Show first 10
            self.stdout.write(f"  - {site.domain} ({site.environment})")
        
        if sites.count() > 10:
            self.stdout.write(f"  ... and {sites.count() - 10} more sites")
        
        # Confirm unless forced
        if not self.options.get('force') and not self.options.get('dry_run'):
            confirm = input("\nProceed? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("Operation cancelled.")
                return
        
        # Execute operation
        result = await sites.enable_maintenance(
            reason=self.options['reason'],
            message=self.options.get('message'),
            user=user,
            dry_run=self.options.get('dry_run', False)
        )
        
        # Display results
        self._display_bulk_result("Enable Maintenance", result)
    
    async def _handle_disable(self, user: User):
        """Handle disable maintenance action."""
        sites = self._get_sites_queryset(user).in_maintenance()
        
        if sites.count() == 0:
            self.stdout.write(self.style.WARNING("No sites in maintenance match the specified filters."))
            return
        
        # Show what will be affected
        self.stdout.write(f"Will disable maintenance for {sites.count()} sites:")
        for site in sites.all()[:10]:
            duration = site.maintenance_duration
            duration_str = f" ({duration})" if duration else ""
            self.stdout.write(f"  - {site.domain}{duration_str}")
        
        if sites.count() > 10:
            self.stdout.write(f"  ... and {sites.count() - 10} more sites")
        
        # Confirm unless forced
        if not self.options.get('force') and not self.options.get('dry_run'):
            confirm = input("\nProceed? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("Operation cancelled.")
                return
        
        # Execute operation
        result = await sites.disable_maintenance(
            user=user,
            dry_run=self.options.get('dry_run', False)
        )
        
        # Display results
        self._display_bulk_result("Disable Maintenance", result)
    
    async def _handle_status(self, user: User):
        """Handle status check action."""
        sites = self._get_sites_queryset(user)
        
        if sites.count() == 0:
            self.stdout.write(self.style.WARNING("No sites match the specified filters."))
            return
        
        self.stdout.write(f"Checking status of {sites.count()} sites...")
        
        result = await sites.check_status()
        
        # Display status summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Status check completed for {result['total']} sites"))
        
        status_summary = result.get('status_summary', {})
        if status_summary:
            self.stdout.write("\nStatus Summary:")
            for status, count in status_summary.items():
                self.stdout.write(f"  {status.title()}: {count} sites")
        
        # Display individual site status if verbose
        if self.options.get('verbose'):
            self.stdout.write("\nIndividual Site Status:")
            for site_info in result.get('sites', []):
                status_icon = {
                    'active': '🟢',
                    'maintenance': '🔧',
                    'offline': '🔴',
                    'unknown': '❓',
                    'error': '❌'
                }.get(site_info['status'], '❓')
                
                self.stdout.write(
                    f"  {status_icon} {site_info['domain']}: {site_info['status']}"
                )
    
    def _handle_list(self, user: User):
        """Handle list sites action."""
        sites = self._get_sites_queryset(user)
        
        if sites.count() == 0:
            self.stdout.write(self.style.WARNING("No sites match the specified filters."))
            return
        
        # Display sites in table format
        self.stdout.write(f"\nFound {sites.count()} sites:\n")
        
        # Header
        self.stdout.write(
            f"{'Domain':<30} {'Environment':<12} {'Status':<12} {'Project':<20} {'Maintenance':<12}"
        )
        self.stdout.write("-" * 86)
        
        # Sites
        for site in sites.all():
            maintenance_status = "Active" if site.maintenance_active else "Inactive"
            
            self.stdout.write(
                f"{site.domain:<30} {site.environment:<12} {site.current_status:<12} "
                f"{(site.project or 'None'):<20} {maintenance_status:<12}"
            )
    
    async def _handle_discover(self, user: User):
        """Handle site discovery action."""
        api_token = self.options.get('api_token')
        if not api_token:
            raise CommandError("--api-token is required for site discovery")
        
        self.stdout.write("Discovering Cloudflare sites...")
        
        try:
            discovered_sites = await multi_site_manager.discover_sites(api_token, user)
            
            if discovered_sites:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Discovered {len(discovered_sites)} new sites:")
                )
                for site in discovered_sites:
                    self.stdout.write(f"  - {site.domain} ({site.environment})")
            else:
                self.stdout.write(self.style.WARNING("No new sites discovered."))
                
        except Exception as e:
            raise CommandError(f"Site discovery failed: {str(e)}")
    
    def _display_bulk_result(self, operation: str, result):
        """Display bulk operation results."""
        if result.dry_run:
            self.stdout.write(self.style.WARNING(f"\n🔍 DRY RUN - {operation}"))
            self.stdout.write(f"Would affect {len(result.would_affect)} sites:")
            for domain in result.would_affect[:10]:
                self.stdout.write(f"  - {domain}")
            if len(result.would_affect) > 10:
                self.stdout.write(f"  ... and {len(result.would_affect) - 10} more")
            return
        
        # Real operation results
        self.stdout.write(f"\n{operation} Results:")
        self.stdout.write(f"Total sites: {result.total}")
        
        if result.successful:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successful: {len(result.successful)} sites")
            )
            if self.options.get('verbose'):
                for domain in result.successful:
                    self.stdout.write(f"  ✅ {domain}")
        
        if result.failed:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed: {len(result.failed)} sites")
            )
            for failure in result.failed:
                self.stdout.write(f"  ❌ {failure['site']}: {failure['reason']}")
        
        if result.skipped:
            self.stdout.write(
                self.style.WARNING(f"⏭️  Skipped: {len(result.skipped)} sites")
            )
            if self.options.get('verbose'):
                for skip in result.skipped:
                    self.stdout.write(f"  ⏭️  {skip['site']}: {skip['reason']}")
        
        # Success rate
        success_rate = result.success_rate
        if success_rate == 100.0:
            style = self.style.SUCCESS
        elif success_rate >= 80.0:
            style = self.style.WARNING
        else:
            style = self.style.ERROR
        
        self.stdout.write(style(f"\nSuccess rate: {success_rate:.1f}%"))
