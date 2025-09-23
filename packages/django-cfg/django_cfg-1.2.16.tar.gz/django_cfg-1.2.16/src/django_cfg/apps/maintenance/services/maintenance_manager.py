"""
Modern maintenance mode manager using official Cloudflare library.

Provides clean, reliable maintenance mode management with Workers and Page Rules.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.utils import timezone
from django.db import transaction

from .cloudflare_client import CloudflareClient
from ..models import CloudflareSite, MaintenanceEvent, CloudflareDeployment
from django_cfg.models.cloudflare import CloudflareConfig

logger = logging.getLogger(__name__)


class MaintenanceManager:
    """
    Modern maintenance mode manager using Cloudflare Workers.
    
    Provides reliable maintenance mode with automatic rollback capabilities.
    """
    
    # Modern maintenance page template
    MAINTENANCE_WORKER_TEMPLATE = '''
addEventListener('fetch', event => {
  event.respondWith(handleMaintenanceMode(event.request))
})

async function handleMaintenanceMode(request) {
  const maintenanceHtml = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Maintenance Mode - {site_name}</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 20px;
            }
            .container {
                max-width: 600px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 60px 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                font-weight: 300;
            }
            .icon {
                font-size: 4rem;
                margin-bottom: 30px;
                opacity: 0.8;
            }
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .message {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #fff;
            }
            .footer {
                margin-top: 40px;
                font-size: 0.9rem;
                opacity: 0.7;
            }
            @media (max-width: 768px) {
                h1 { font-size: 2rem; }
                .container { padding: 40px 20px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🔧</div>
            <h1>Under Maintenance</h1>
            <p>We're currently performing scheduled maintenance to improve your experience.</p>
            
            <div class="message">
                <strong>{maintenance_message}</strong>
            </div>
            
            <p>We'll be back online shortly. Thank you for your patience!</p>
            
            <div class="footer">
                <p>Started: {started_at}<br>
                Estimated completion: {estimated_completion}</p>
            </div>
        </div>
    </body>
    </html>
  `
  
  return new Response(maintenanceHtml, {
    status: 503,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
      'Retry-After': '3600'
    }
  })
}
'''
    
    def __init__(self, config: CloudflareConfig):
        """Initialize maintenance manager."""
        self.config = config
        self.client = CloudflareClient(config)
        
    def enable_maintenance(
        self,
        site: CloudflareSite,
        maintenance_event: MaintenanceEvent,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enable maintenance mode for a site using Cloudflare Workers.
        
        Args:
            site: CloudflareSite to enable maintenance for
            maintenance_event: MaintenanceEvent record
            custom_message: Custom maintenance message
            
        Returns:
            Dict with deployment results
        """
        logger.info(f"Enabling maintenance mode for {site.domain}")
        
        try:
            with transaction.atomic():
                # Get account ID
                account_id = site.account_id or self.client.get_account_id()
                if not account_id:
                    raise ValueError("No account ID available")
                
                # Prepare worker script
                worker_name = f"maintenance-{site.domain.replace('.', '-')}"
                worker_script = self._prepare_worker_script(
                    site=site,
                    maintenance_event=maintenance_event,
                    custom_message=custom_message
                )
                
                # Deploy worker
                worker_result = self.client.create_worker(
                    account_id=account_id,
                    script_name=worker_name,
                    script_content=worker_script
                )
                
                # Create worker route
                route_pattern = f"{site.domain}/*"
                route_result = self.client.create_worker_route(
                    zone_id=site.zone_id,
                    pattern=route_pattern,
                    script_name=worker_name
                )
                
                # Create deployment record
                deployment = CloudflareDeployment.objects.create_deployment(
                    site=site,
                    deployment_type='worker',
                    cloudflare_id=worker_result.id,
                    config={
                        'worker_name': worker_name,
                        'route_pattern': route_pattern,
                        'route_id': route_result.get('id'),
                        'maintenance_event_id': maintenance_event.id,
                        'custom_message': custom_message
                    },
                    maintenance_event=maintenance_event
                )
                
                # Update site maintenance status
                site.maintenance_active = True
                site.last_maintenance_at = timezone.now()
                site.save()
                
                # Update maintenance event
                maintenance_event.status = MaintenanceEvent.Status.ACTIVE
                maintenance_event.started_at = timezone.now()
                maintenance_event.save()
                
                logger.info(f"Maintenance mode enabled for {site.domain}")
                
                return {
                    'success': True,
                    'deployment_id': deployment.id,
                    'worker_name': worker_name,
                    'route_pattern': route_pattern,
                    'message': f"Maintenance mode enabled for {site.domain}"
                }
                
        except Exception as e:
            logger.error(f"Failed to enable maintenance for {site.domain}: {e}")
            
            # Update maintenance event status
            maintenance_event.status = MaintenanceEvent.Status.FAILED
            maintenance_event.error_message = str(e)
            maintenance_event.save()
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to enable maintenance for {site.domain}"
            }
    
    def disable_maintenance(
        self,
        site: CloudflareSite,
        maintenance_event: Optional[MaintenanceEvent] = None
    ) -> Dict[str, Any]:
        """
        Disable maintenance mode for a site.
        
        Args:
            site: CloudflareSite to disable maintenance for
            maintenance_event: Optional MaintenanceEvent to update
            
        Returns:
            Dict with results
        """
        logger.info(f"Disabling maintenance mode for {site.domain}")
        
        try:
            with transaction.atomic():
                # Find active maintenance deployments
                active_deployments = CloudflareDeployment.objects.filter(
                    site=site,
                    deployment_type='worker',
                    status='active'
                )
                
                results = []
                account_id = site.account_id or self.client.get_account_id()
                
                for deployment in active_deployments:
                    try:
                        config = deployment.config or {}
                        worker_name = config.get('worker_name')
                        route_id = config.get('route_id')
                        
                        # Delete worker route
                        if route_id:
                            self.client.delete_worker_route(site.zone_id, route_id)
                        
                        # Delete worker script
                        if worker_name and account_id:
                            self.client.delete_worker(account_id, worker_name)
                        
                        # Update deployment status
                        deployment.status = 'rolled_back'
                        deployment.save()
                        
                        results.append({
                            'deployment_id': deployment.id,
                            'worker_name': worker_name,
                            'success': True
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to cleanup deployment {deployment.id}: {e}")
                        results.append({
                            'deployment_id': deployment.id,
                            'success': False,
                            'error': str(e)
                        })
                
                # Update site maintenance status
                site.maintenance_active = False
                site.save()
                
                # Update maintenance event if provided
                if maintenance_event:
                    maintenance_event.status = MaintenanceEvent.Status.COMPLETED
                    maintenance_event.ended_at = timezone.now()
                    maintenance_event.save()
                
                logger.info(f"Maintenance mode disabled for {site.domain}")
                
                return {
                    'success': True,
                    'deployments_cleaned': len([r for r in results if r['success']]),
                    'cleanup_results': results,
                    'message': f"Maintenance mode disabled for {site.domain}"
                }
                
        except Exception as e:
            logger.error(f"Failed to disable maintenance for {site.domain}: {e}")
            
            if maintenance_event:
                maintenance_event.status = MaintenanceEvent.Status.FAILED
                maintenance_event.error_message = str(e)
                maintenance_event.save()
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to disable maintenance for {site.domain}"
            }
    
    def bulk_enable_maintenance(
        self,
        sites: List[CloudflareSite],
        maintenance_event: MaintenanceEvent,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enable maintenance mode for multiple sites.
        
        Args:
            sites: List of CloudflareSite objects
            maintenance_event: MaintenanceEvent record
            custom_message: Custom maintenance message
            
        Returns:
            Dict with bulk operation results
        """
        logger.info(f"Enabling maintenance mode for {len(sites)} sites")
        
        results = {
            'success': 0,
            'failed': 0,
            'sites': []
        }
        
        for site in sites:
            try:
                result = self.enable_maintenance(
                    site=site,
                    maintenance_event=maintenance_event,
                    custom_message=custom_message
                )
                
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                results['sites'].append({
                    'site_id': site.id,
                    'domain': site.domain,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Bulk maintenance failed for {site.domain}: {e}")
                results['failed'] += 1
                results['sites'].append({
                    'site_id': site.id,
                    'domain': site.domain,
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        logger.info(f"Bulk maintenance completed: {results['success']} success, {results['failed']} failed")
        return results
    
    def bulk_disable_maintenance(
        self,
        sites: List[CloudflareSite],
        maintenance_event: Optional[MaintenanceEvent] = None
    ) -> Dict[str, Any]:
        """
        Disable maintenance mode for multiple sites.
        
        Args:
            sites: List of CloudflareSite objects
            maintenance_event: Optional MaintenanceEvent to update
            
        Returns:
            Dict with bulk operation results
        """
        logger.info(f"Disabling maintenance mode for {len(sites)} sites")
        
        results = {
            'success': 0,
            'failed': 0,
            'sites': []
        }
        
        for site in sites:
            try:
                result = self.disable_maintenance(
                    site=site,
                    maintenance_event=maintenance_event
                )
                
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                results['sites'].append({
                    'site_id': site.id,
                    'domain': site.domain,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Bulk maintenance disable failed for {site.domain}: {e}")
                results['failed'] += 1
                results['sites'].append({
                    'site_id': site.id,
                    'domain': site.domain,
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        logger.info(f"Bulk maintenance disable completed: {results['success']} success, {results['failed']} failed")
        return results
    
    def _prepare_worker_script(
        self,
        site: CloudflareSite,
        maintenance_event: MaintenanceEvent,
        custom_message: Optional[str] = None
    ) -> str:
        """Prepare Worker script with site-specific content."""
        message = custom_message or maintenance_event.maintenance_message or "Scheduled maintenance in progress"
        
        started_at = maintenance_event.started_at or timezone.now()
        estimated_completion = "Soon"
        
        if maintenance_event.estimated_duration:
            completion_time = started_at + maintenance_event.estimated_duration
            estimated_completion = completion_time.strftime("%Y-%m-%d %H:%M UTC")
        
        return self.MAINTENANCE_WORKER_TEMPLATE.format(
            site_name=site.name or site.domain,
            maintenance_message=message,
            started_at=started_at.strftime("%Y-%m-%d %H:%M UTC"),
            estimated_completion=estimated_completion
        )
    
    def get_maintenance_status(self, site: CloudflareSite) -> Dict[str, Any]:
        """
        Get current maintenance status for a site.
        
        Args:
            site: CloudflareSite to check
            
        Returns:
            Dict with maintenance status
        """
        active_deployments = CloudflareDeployment.objects.filter(
            site=site,
            deployment_type='worker',
            status='active'
        ).with_maintenance_event()
        
        if not active_deployments.exists():
            return {
                'maintenance_active': False,
                'site_id': site.id,
                'domain': site.domain
            }
        
        deployment = active_deployments.first()
        maintenance_event = deployment.maintenance_event
        
        return {
            'maintenance_active': True,
            'site_id': site.id,
            'domain': site.domain,
            'deployment_id': deployment.id,
            'started_at': deployment.deployed_at.isoformat(),
            'maintenance_event': {
                'id': maintenance_event.id if maintenance_event else None,
                'title': maintenance_event.title if maintenance_event else None,
                'status': maintenance_event.status if maintenance_event else None,
                'estimated_duration': str(maintenance_event.estimated_duration) if maintenance_event and maintenance_event.estimated_duration else None
            } if maintenance_event else None,
            'worker_config': deployment.config
        }
