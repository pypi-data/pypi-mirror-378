"""
Super simple maintenance service using Page Rules.

No Workers, no templates, no complexity - just Page Rules!
"""

import logging
import time
from typing import Dict, Any
from cloudflare import Cloudflare

from ..models import CloudflareSite, MaintenanceLog
from ..utils import retry_on_failure

logger = logging.getLogger(__name__)

class MaintenanceService:
    """
    Simple maintenance via Cloudflare Page Rules.
    
    Enable: Create Page Rule redirect to maintenance.reforms.ai
    Disable: Delete Page Rule
    """
    
    def __init__(self, site: CloudflareSite):
        """Initialize service for specific site."""
        self.site = site
        self.client = Cloudflare(api_token=site.api_key.api_token)
    
    def enable_maintenance(self, reason: str = "Scheduled maintenance") -> MaintenanceLog:
        """
        Enable maintenance mode using Page Rule redirect.
        
        Steps:
        1. Create Page Rule redirect to maintenance.reforms.ai
        2. Update site.maintenance_active = True
        3. Log the operation
        """
        start_time = time.time()
        log_entry = MaintenanceLog.log_pending(self.site, MaintenanceLog.Action.ENABLE, reason)
        
        try:
            # 1. Create Page Rule for maintenance redirect
            logger.info(f"Creating page rule for: {self.site.domain} → {self.site.get_maintenance_url()}")
            page_rule_response = self._create_maintenance_page_rule()
            
            # 2. Update site status
            self.site.enable_maintenance()
            
            # 3. Log success
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.SUCCESS
            log_entry.duration_seconds = duration
            log_entry.cloudflare_response = {
                'page_rule_create': self._serialize_response(page_rule_response)
            }
            log_entry.save()
            
            return log_entry
            
        except Exception as e:
            # Log failure
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.FAILED
            log_entry.error_message = str(e)
            log_entry.duration_seconds = duration
            log_entry.save()
            
            raise e
    
    def disable_maintenance(self) -> MaintenanceLog:
        """
        Disable maintenance mode by removing Page Rule.
        
        Steps:
        1. Remove Page Rule redirect
        2. Update site.maintenance_active = False  
        3. Log the operation
        """
        start_time = time.time()
        log_entry = MaintenanceLog.log_pending(self.site, MaintenanceLog.Action.DISABLE)
        
        try:
            # 1. Remove Page Rule
            logger.info(f"Removing page rule for: {self.site.domain}")
            page_rule_response = self._delete_maintenance_page_rule()
            
            # 2. Update site status
            self.site.disable_maintenance()
            
            # 3. Log success
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.SUCCESS
            log_entry.duration_seconds = duration
            log_entry.cloudflare_response = {
                'page_rule_delete': self._serialize_response(page_rule_response)
            }
            log_entry.save()
            
            return log_entry
            
        except Exception as e:
            # Log failure
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.FAILED
            log_entry.error_message = str(e)
            log_entry.duration_seconds = duration
            log_entry.save()
            
            raise e
    
    def get_status(self) -> bool:
        """Get current maintenance status for site."""
        return self.site.maintenance_active
    
    # Private helper methods
    
    def _serialize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Cloudflare API response to JSON serializable format."""
        import json
        from datetime import datetime
        
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        try:
            # Convert all datetime objects to ISO strings
            serializable = convert_datetime(response)
            # Test JSON serialization
            json.dumps(serializable)
            return serializable
        except Exception:
            # If serialization fails, return simple success message
            return {"success": True, "serialization_error": True}
    
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def _create_maintenance_page_rule(self) -> Dict[str, Any]:
        """Create Page Rule to redirect all traffic to maintenance page."""
        maintenance_url = self.site.get_maintenance_url()
        pattern = f"{self.site.domain}/*"
        
        logger.info(f"Creating page rule: {pattern} → {maintenance_url}")
        
        response = self.client.page_rules.create(
            zone_id=self.site.zone_id,
            targets=[{
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": pattern
                }
            }],
            actions=[{
                "id": "forwarding_url",
                "value": {
                    "url": maintenance_url,
                    "status_code": 302
                }
            }],
            status="active"
        )
        return response.model_dump()
    
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def _delete_maintenance_page_rule(self) -> Dict[str, Any]:
        """Delete maintenance Page Rule with retry logic."""
        # Find the maintenance page rule
        page_rules_response = self.client.page_rules.list(zone_id=self.site.zone_id)
        
        # Handle different API response formats
        if hasattr(page_rules_response, 'result'):
            page_rules = page_rules_response.result
        else:
            page_rules = page_rules_response
        
        maintenance_pattern = f"{self.site.domain}/*"
        maintenance_url = self.site.get_maintenance_url()
        
        logger.info(f"Looking for page rule to delete: pattern={maintenance_pattern}, url={maintenance_url}")
        logger.info(f"Found {len(page_rules)} page rules total")
        
        for rule in page_rules:
            logger.info(f"Checking rule {rule.id}: targets={getattr(rule, 'targets', None)}, actions={getattr(rule, 'actions', None)}")
            
            # Simple check - look for forwarding_url action with maintenance URL
            if (hasattr(rule, 'actions') and rule.actions and 
                len(rule.actions) > 0 and 
                hasattr(rule.actions[0], 'id') and 
                rule.actions[0].id == "forwarding_url"):
                
                # Check if URL contains maintenance.reforms.ai
                action_value = getattr(rule.actions[0], 'value', {})
                action_url = getattr(action_value, 'url', '')
                
                logger.info(f"Found forwarding rule with URL: {action_url}")
                
                if "maintenance.reforms.ai" in action_url:
                    logger.info(f"Deleting maintenance page rule: {rule.id}")
                    response = self.client.page_rules.delete(
                        zone_id=self.site.zone_id,
                        pagerule_id=rule.id
                    )
                    return response.model_dump()
        
        logger.warning(f"No maintenance page rule found for {self.site.domain}")
        return {"success": True, "message": "No page rule to delete"}
    


# Convenience functions for easy usage

def enable_maintenance_for_domain(domain: str, reason: str = "Scheduled maintenance") -> MaintenanceLog:
    """Enable maintenance for a domain."""
    site = CloudflareSite.objects.get(domain=domain)
    service = MaintenanceService(site)
    return service.enable_maintenance(reason)


def disable_maintenance_for_domain(domain: str) -> MaintenanceLog:
    """Disable maintenance for a domain."""
    site = CloudflareSite.objects.get(domain=domain)
    service = MaintenanceService(site)
    return service.disable_maintenance()
