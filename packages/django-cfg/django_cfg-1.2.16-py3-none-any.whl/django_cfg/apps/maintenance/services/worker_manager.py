"""
Cloudflare Workers management using official library.

Provides clean interface for managing Workers scripts and routes.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .cloudflare_client import CloudflareClient
from django_cfg.models.cloudflare import CloudflareConfig

logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Cloudflare Workers management service.
    
    Provides high-level interface for Workers operations.
    """
    
    def __init__(self, config: CloudflareConfig):
        """Initialize worker manager."""
        self.config = config
        self.client = CloudflareClient(config)
        
    def deploy_worker(
        self,
        account_id: str,
        script_name: str,
        script_content: str,
        routes: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a Worker script with optional routes.
        
        Args:
            account_id: Cloudflare account ID
            script_name: Name for the Worker script
            script_content: JavaScript code for the Worker
            routes: List of route configurations [{'zone_id': '...', 'pattern': '...'}]
            
        Returns:
            Dict with deployment results
        """
        logger.info(f"Deploying Worker script: {script_name}")
        
        try:
            # Deploy the Worker script
            worker_result = self.client.create_worker(
                account_id=account_id,
                script_name=script_name,
                script_content=script_content
            )
            
            deployed_routes = []
            
            # Create routes if provided
            if routes:
                for route_config in routes:
                    try:
                        route_result = self.client.create_worker_route(
                            zone_id=route_config['zone_id'],
                            pattern=route_config['pattern'],
                            script_name=script_name
                        )
                        deployed_routes.append({
                            'zone_id': route_config['zone_id'],
                            'pattern': route_config['pattern'],
                            'route_id': route_result.get('id'),
                            'success': True
                        })
                    except Exception as e:
                        logger.error(f"Failed to create route {route_config['pattern']}: {e}")
                        deployed_routes.append({
                            'zone_id': route_config['zone_id'],
                            'pattern': route_config['pattern'],
                            'success': False,
                            'error': str(e)
                        })
            
            logger.info(f"Successfully deployed Worker: {script_name}")
            
            return {
                'success': True,
                'worker_id': worker_result.id,
                'script_name': script_name,
                'routes': deployed_routes,
                'deployed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy Worker {script_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'script_name': script_name
            }
    
    def update_worker(
        self,
        account_id: str,
        script_name: str,
        script_content: str
    ) -> Dict[str, Any]:
        """
        Update an existing Worker script.
        
        Args:
            account_id: Cloudflare account ID
            script_name: Name of the Worker script to update
            script_content: New JavaScript code
            
        Returns:
            Dict with update results
        """
        logger.info(f"Updating Worker script: {script_name}")
        
        try:
            worker_result = self.client.create_worker(
                account_id=account_id,
                script_name=script_name,
                script_content=script_content
            )
            
            logger.info(f"Successfully updated Worker: {script_name}")
            
            return {
                'success': True,
                'worker_id': worker_result.id,
                'script_name': script_name,
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update Worker {script_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'script_name': script_name
            }
    
    def delete_worker(
        self,
        account_id: str,
        script_name: str,
        cleanup_routes: bool = True
    ) -> Dict[str, Any]:
        """
        Delete a Worker script and optionally its routes.
        
        Args:
            account_id: Cloudflare account ID
            script_name: Name of the Worker script to delete
            cleanup_routes: Whether to delete associated routes
            
        Returns:
            Dict with deletion results
        """
        logger.info(f"Deleting Worker script: {script_name}")
        
        try:
            # TODO: If cleanup_routes is True, we'd need to find and delete routes
            # This would require additional API calls to list routes and filter by script
            
            success = self.client.delete_worker(account_id, script_name)
            
            if success:
                logger.info(f"Successfully deleted Worker: {script_name}")
                return {
                    'success': True,
                    'script_name': script_name,
                    'deleted_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Delete operation returned False',
                    'script_name': script_name
                }
                
        except Exception as e:
            logger.error(f"Failed to delete Worker {script_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'script_name': script_name
            }
    
    def list_workers(self, account_id: str) -> Dict[str, Any]:
        """
        List all Workers in an account.
        
        Args:
            account_id: Cloudflare account ID
            
        Returns:
            Dict with workers list
        """
        logger.info("Listing Workers scripts")
        
        try:
            workers = self.client.list_workers(account_id)
            
            workers_data = []
            for worker in workers:
                workers_data.append({
                    'id': worker.id,
                    'script_name': getattr(worker, 'script_name', ''),
                    'created_on': getattr(worker, 'created_on', ''),
                    'modified_on': getattr(worker, 'modified_on', ''),
                    'size': getattr(worker, 'size', 0)
                })
            
            logger.info(f"Found {len(workers_data)} Workers")
            
            return {
                'success': True,
                'workers': workers_data,
                'count': len(workers_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to list Workers: {e}")
            return {
                'success': False,
                'error': str(e),
                'workers': [],
                'count': 0
            }
    
    def get_worker_analytics(
        self,
        account_id: str,
        script_name: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a Worker script.
        
        Note: This would require additional API calls to Cloudflare Analytics API
        which might not be available in the basic cloudflare library.
        
        Args:
            account_id: Cloudflare account ID
            script_name: Worker script name
            since: Start date for analytics
            until: End date for analytics
            
        Returns:
            Dict with analytics data
        """
        logger.info(f"Getting analytics for Worker: {script_name}")
        
        # This is a placeholder - actual implementation would require
        # additional API calls to Cloudflare Analytics API
        return {
            'success': False,
            'error': 'Analytics API not implemented yet',
            'script_name': script_name
        }
