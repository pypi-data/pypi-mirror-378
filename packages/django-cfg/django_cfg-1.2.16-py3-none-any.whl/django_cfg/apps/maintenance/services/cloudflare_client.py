"""
Modern Cloudflare client using cloudflare v4.x library.

Provides a clean, type-safe wrapper around the latest Cloudflare Python SDK.
Supports all major Cloudflare API operations with proper error handling and retry logic.
"""

import logging
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
from datetime import datetime
import time
import random

try:
    from cloudflare import Cloudflare
    # Note: Using Any for types as cloudflare 4.x has different type structure
    # We'll handle typing at runtime
except ImportError:
    raise ImportError(
        "cloudflare library is required. Install with: pip install cloudflare>=4.3.0"
    )

from django_cfg.models.cloudflare import CloudflareConfig

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on_status: List[int] = None

    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = [429, 502, 503, 504]


class CloudflareClient:
    """
    Modern Cloudflare client using v4.x library.
    
    Provides rate limiting, retry logic, and clean API access with proper typing.
    """
    
    def __init__(
        self, 
        config: CloudflareConfig,
        retry_config: Optional[RetryConfig] = None
    ):
        """Initialize Cloudflare client."""
        self.config = config
        self.retry_config = retry_config or RetryConfig()
        
        # Initialize official Cloudflare client (v4.x API)
        self.client = Cloudflare(
            api_token=config.get_api_token(),
            max_retries=self.retry_config.max_retries
        )
        
        # Rate limiting state
        self._last_request_time = 0
        self._request_count = 0
        
        logger.info("Cloudflare client v4.x initialized")
    
    # === Zone Management ===
    
    def list_zones(self, **kwargs) -> List[Any]:
        """List all zones in the account."""
        zones = []
        try:
            # Use the paginated iterator
            for zone in self.client.zones.list(**kwargs):
                zones.append(zone)
            return zones
        except Exception as e:
            logger.error(f"Failed to list zones: {e}")
            return []
    
    def get_zone(self, zone_id: str) -> Optional[Any]:
        """Get zone by ID."""
        try:
            return self._execute_with_retry(
                lambda: self.client.zones.get(zone_id=zone_id)
            )
        except Exception as e:
            logger.warning(f"Zone {zone_id} not found: {e}")
            return None
    
    def get_zone_by_name(self, domain: str) -> Optional[Any]:
        """Get zone by domain name."""
        try:
            zones = list(self.client.zones.list(name=domain))
            return zones[0] if zones else None
        except Exception as e:
            logger.warning(f"Zone for domain {domain} not found: {e}")
            return None
    
    # === DNS Management ===
    
    def list_dns_records(
        self, 
        zone_id: str, 
        record_type: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> List[Any]:
        """List DNS records for a zone."""
        params = kwargs.copy()
        if record_type:
            params['type'] = record_type
        if name:
            params['name'] = name
            
        records = []
        try:
            for record in self.client.dns.records.list(zone_id=zone_id, **params):
                records.append(record)
            return records
        except Exception as e:
            logger.error(f"Failed to list DNS records for zone {zone_id}: {e}")
            return []
    
    def create_dns_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
        proxied: Optional[bool] = None,
        **kwargs
    ) -> Optional[Any]:
        """Create a DNS record."""
        record_data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            **kwargs
        }
        
        # Only set proxied for supported record types
        if proxied is not None and record_type.upper() in ['A', 'AAAA', 'CNAME']:
            record_data['proxied'] = proxied
        
        try:
            return self._execute_with_retry(
                lambda: self.client.dns.records.create(zone_id=zone_id, **record_data)
            )
        except Exception as e:
            logger.error(f"Failed to create DNS record: {e}")
            return None
    
    def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        **kwargs
    ) -> Optional[Any]:
        """Update a DNS record."""
        try:
            return self._execute_with_retry(
                lambda: self.client.dns.records.update(
                    dns_record_id=record_id, zone_id=zone_id, **kwargs
                )
            )
        except Exception as e:
            logger.error(f"Failed to update DNS record {record_id}: {e}")
            return None
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """Delete a DNS record."""
        try:
            self._execute_with_retry(
                lambda: self.client.dns.records.delete(
                    dns_record_id=record_id, zone_id=zone_id
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete DNS record {record_id}: {e}")
            return False
    
    # === Workers Management ===
    
    def list_workers(self, account_id: str) -> List[Any]:
        """List all Workers scripts."""
        scripts = []
        try:
            for script in self.client.workers.scripts.list(account_id=account_id):
                scripts.append(script)
            return scripts
        except Exception as e:
            logger.error(f"Failed to list workers for account {account_id}: {e}")
            return []
    
    def create_worker(
        self,
        account_id: str,
        script_name: str,
        script_content: str,
        **kwargs
    ) -> Optional[Any]:
        """Create or update a Worker script."""
        try:
            return self._execute_with_retry(
                lambda: self.client.workers.scripts.update(
                    script_name=script_name,
                    account_id=account_id,
                    body=script_content,
                    **kwargs
                )
            )
        except Exception as e:
            logger.error(f"Failed to create/update worker {script_name}: {e}")
            return None
    
    def delete_worker(self, account_id: str, script_name: str) -> bool:
        """Delete a Worker script."""
        try:
            self._execute_with_retry(
                lambda: self.client.workers.scripts.delete(
                    script_name=script_name, account_id=account_id
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete worker {script_name}: {e}")
            return False
    
    def create_worker_route(
        self,
        zone_id: str,
        pattern: str,
        script_name: str
    ) -> Optional[Dict[str, Any]]:
        """Create a Worker route."""
        try:
            return self._execute_with_retry(
                lambda: self.client.workers.routes.create(
                    zone_id=zone_id,
                    pattern=pattern,
                    script=script_name
                )
            )
        except Exception as e:
            logger.error(f"Failed to create worker route: {e}")
            return None
    
    def delete_worker_route(self, zone_id: str, route_id: str) -> bool:
        """Delete a Worker route."""
        try:
            self._execute_with_retry(
                lambda: self.client.workers.routes.delete(
                    route_id=route_id, zone_id=zone_id
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete worker route {route_id}: {e}")
            return False
    
    # === Account Information ===
    
    def get_account_info(self) -> List[Dict[str, Any]]:
        """Get account information."""
        accounts = []
        try:
            for account in self.client.accounts.list():
                accounts.append(account.model_dump())
            return accounts
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return []
    
    def get_account_id(self) -> Optional[str]:
        """Get the first account ID."""
        try:
            accounts = list(self.client.accounts.list())
            return accounts[0].id if accounts else None
        except Exception as e:
            logger.error(f"Failed to get account ID: {e}")
            return None
    
    # === Zone Serialization ===
    
    def serialize_zone(self, zone: Any) -> Dict[str, Any]:
        """Serialize Zone object to dict."""
        try:
            zone_dict = zone.model_dump()
            
            # Ensure account info is properly serialized
            if hasattr(zone, 'account') and zone.account:
                zone_dict['account'] = zone.account.model_dump()
            
            return zone_dict
        except Exception as e:
            logger.warning(f"Failed to serialize zone {zone.name}: {e}")
            return {
                'id': zone.id,
                'name': zone.name,
                'status': zone.status,
                'error': f"Serialization failed: {e}"
            }
    
    # === Rate Limiting & Retry Logic ===
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic and rate limiting."""
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Rate limiting check
                self._check_rate_limit()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Update success stats
                self._update_request_stats(success=True)
                
                return result
                
            except Exception as e:
                self._update_request_stats(success=False)
                last_exception = e
                
                # Check if we should retry
                if not self._should_retry(e, attempt):
                    break
                
                # Calculate delay and wait
                if attempt < self.retry_config.max_retries:
                    delay = self._calculate_retry_delay(attempt, e)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
        
        # All retries exhausted
        logger.error(f"Request failed after {self.retry_config.max_retries} retries: {last_exception}")
        raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry the request."""
        if attempt >= self.retry_config.max_retries:
            return False
        
        # Check for Cloudflare API exceptions
        if hasattr(exception, 'status_code'):
            return exception.status_code in self.retry_config.retry_on_status
        
        # Retry on network errors
        error_str = str(exception).lower()
        if any(keyword in error_str for keyword in ['network', 'timeout', 'connection']):
            return True
        
        return False
    
    def _calculate_retry_delay(self, attempt: int, exception: Exception = None) -> float:
        """Calculate delay for retry with exponential backoff."""
        # Exponential backoff with jitter
        delay = self.retry_config.base_delay * (
            self.retry_config.backoff_factor ** attempt
        )
        
        if self.retry_config.jitter:
            jitter_factor = random.uniform(0.5, 1.5)
            delay *= jitter_factor
        
        return min(delay, self.retry_config.max_delay)
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        # Simple rate limiting: max 4 requests per second
        min_interval = 0.25
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _update_request_stats(self, success: bool):
        """Update request statistics."""
        self._request_count += 1
        
        if success:
            logger.debug(f"Request #{self._request_count} successful")
        else:
            logger.debug(f"Request #{self._request_count} failed")
    
    # === Health Check ===
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the Cloudflare API."""
        try:
            start_time = time.time()
            
            # Simple API call to check connectivity
            zones = list(self.client.zones.list())
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'zones_count': len(zones),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # === Context Manager Support ===
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self.client, 'close'):
            self.client.close()
