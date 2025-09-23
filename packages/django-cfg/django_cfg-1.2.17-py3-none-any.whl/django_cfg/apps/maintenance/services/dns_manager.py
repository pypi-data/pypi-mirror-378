"""
DNS management service using official Cloudflare library.

Provides high-level DNS operations with validation and bulk operations.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .cloudflare_client import CloudflareClient
from django_cfg.models.cloudflare import CloudflareConfig

logger = logging.getLogger(__name__)


class DNSManager:
    """
    DNS management service for Cloudflare.
    
    Provides high-level DNS operations with validation and error handling.
    """
    
    # Common DNS record types and their validation
    RECORD_TYPES = {
        'A': {'requires_ip': True, 'supports_proxy': True},
        'AAAA': {'requires_ip': True, 'supports_proxy': True},
        'CNAME': {'requires_domain': True, 'supports_proxy': True},
        'MX': {'requires_priority': True, 'supports_proxy': False},
        'TXT': {'supports_proxy': False},
        'NS': {'supports_proxy': False},
        'SRV': {'requires_priority': True, 'supports_proxy': False},
        'CAA': {'supports_proxy': False},
        'PTR': {'supports_proxy': False}
    }
    
    def __init__(self, config: CloudflareConfig):
        """Initialize DNS manager."""
        self.config = config
        self.client = CloudflareClient(config)
        
    def create_dns_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
        proxied: Optional[bool] = None,
        priority: Optional[int] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Create a DNS record with validation.
        
        Args:
            zone_id: Cloudflare zone ID
            record_type: DNS record type (A, CNAME, etc.)
            name: Record name
            content: Record content
            ttl: Time to live (300-86400)
            proxied: Whether to proxy through Cloudflare
            priority: Priority for MX/SRV records
            validate: Whether to validate record before creation
            
        Returns:
            Dict with creation results
        """
        logger.info(f"Creating DNS record: {record_type} {name}")
        
        try:
            # Validate record if requested
            if validate:
                validation_result = self._validate_record(
                    record_type, name, content, ttl, proxied, priority
                )
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'error': f"Validation failed: {validation_result['error']}",
                        'record_type': record_type,
                        'name': name
                    }
            
            # Determine proxied setting
            if proxied is None:
                proxied = self._should_proxy_record(record_type)
            
            # Create the record
            record = self.client.create_dns_record(
                zone_id=zone_id,
                record_type=record_type,
                name=name,
                content=content,
                ttl=ttl,
                proxied=proxied,
                priority=priority
            )
            
            logger.info(f"Successfully created DNS record: {record.id}")
            
            return {
                'success': True,
                'record_id': record.id,
                'record_type': record_type,
                'name': name,
                'content': content,
                'ttl': ttl,
                'proxied': proxied,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create DNS record {name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_type': record_type,
                'name': name
            }
    
    def bulk_create_records(
        self,
        zone_id: str,
        records: List[Dict[str, Any]],
        validate_all: bool = True,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        Create multiple DNS records in bulk.
        
        Args:
            zone_id: Cloudflare zone ID
            records: List of record configurations
            validate_all: Whether to validate all records before creating any
            stop_on_error: Whether to stop on first error
            
        Returns:
            Dict with bulk operation results
        """
        logger.info(f"Creating {len(records)} DNS records in bulk")
        
        results = {
            'success': 0,
            'failed': 0,
            'records': [],
            'errors': []
        }
        
        # Validate all records first if requested
        if validate_all:
            for i, record_config in enumerate(records):
                validation = self._validate_record_config(record_config)
                if not validation['valid']:
                    error_msg = f"Record {i+1} validation failed: {validation['error']}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    
                    if stop_on_error:
                        return {
                            'success': False,
                            'error': error_msg,
                            'results': results
                        }
        
        # Create records
        for i, record_config in enumerate(records):
            try:
                result = self.create_dns_record(
                    zone_id=zone_id,
                    validate=not validate_all,  # Skip individual validation if we validated all
                    **record_config
                )
                
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    if stop_on_error:
                        return {
                            'success': False,
                            'error': result['error'],
                            'results': results
                        }
                
                results['records'].append({
                    'index': i,
                    'config': record_config,
                    'result': result
                })
                
            except Exception as e:
                error_msg = f"Record {i+1} creation failed: {e}"
                logger.error(error_msg)
                results['failed'] += 1
                results['errors'].append(error_msg)
                results['records'].append({
                    'index': i,
                    'config': record_config,
                    'result': {'success': False, 'error': str(e)}
                })
                
                if stop_on_error:
                    return {
                        'success': False,
                        'error': error_msg,
                        'results': results
                    }
        
        logger.info(f"Bulk DNS creation completed: {results['success']} success, {results['failed']} failed")
        
        return {
            'success': results['failed'] == 0,
            'results': results
        }
    
    def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing DNS record.
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID to update
            **kwargs: Fields to update
            
        Returns:
            Dict with update results
        """
        logger.info(f"Updating DNS record: {record_id}")
        
        try:
            record = self.client.update_dns_record(
                zone_id=zone_id,
                record_id=record_id,
                **kwargs
            )
            
            logger.info(f"Successfully updated DNS record: {record_id}")
            
            return {
                'success': True,
                'record_id': record_id,
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update DNS record {record_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_id': record_id
            }
    
    def delete_dns_record(
        self,
        zone_id: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Delete a DNS record.
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID to delete
            
        Returns:
            Dict with deletion results
        """
        logger.info(f"Deleting DNS record: {record_id}")
        
        try:
            success = self.client.delete_dns_record(zone_id, record_id)
            
            if success:
                logger.info(f"Successfully deleted DNS record: {record_id}")
                return {
                    'success': True,
                    'record_id': record_id,
                    'deleted_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Delete operation returned False',
                    'record_id': record_id
                }
                
        except Exception as e:
            logger.error(f"Failed to delete DNS record {record_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_id': record_id
            }
    
    def get_dns_records(
        self,
        zone_id: str,
        record_type: Optional[str] = None,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get DNS records for a zone.
        
        Args:
            zone_id: Cloudflare zone ID
            record_type: Filter by record type
            name: Filter by record name
            
        Returns:
            Dict with DNS records
        """
        logger.info(f"Getting DNS records for zone: {zone_id}")
        
        try:
            records = self.client.list_dns_records(
                zone_id=zone_id,
                record_type=record_type,
                name=name
            )
            
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'type': record.type,
                    'name': record.name,
                    'content': record.content,
                    'ttl': getattr(record, 'ttl', 300),
                    'proxied': getattr(record, 'proxied', False),
                    'created_on': getattr(record, 'created_on', ''),
                    'modified_on': getattr(record, 'modified_on', ''),
                    'priority': getattr(record, 'priority', None)
                })
            
            logger.info(f"Found {len(records_data)} DNS records")
            
            return {
                'success': True,
                'records': records_data,
                'count': len(records_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get DNS records: {e}")
            return {
                'success': False,
                'error': str(e),
                'records': [],
                'count': 0
            }
    
    def setup_common_records(
        self,
        zone_id: str,
        domain: str,
        server_ip: str,
        mail_server: Optional[str] = None,
        include_www: bool = True
    ) -> Dict[str, Any]:
        """
        Set up common DNS records for a domain.
        
        Args:
            zone_id: Cloudflare zone ID
            domain: Domain name
            server_ip: Server IP address
            mail_server: Mail server hostname
            include_www: Whether to include www CNAME
            
        Returns:
            Dict with setup results
        """
        logger.info(f"Setting up common DNS records for: {domain}")
        
        records_to_create = [
            {
                'record_type': 'A',
                'name': domain,
                'content': server_ip,
                'proxied': True
            }
        ]
        
        if include_www:
            records_to_create.append({
                'record_type': 'CNAME',
                'name': f'www.{domain}',
                'content': domain,
                'proxied': True
            })
        
        if mail_server:
            records_to_create.extend([
                {
                    'record_type': 'MX',
                    'name': domain,
                    'content': mail_server,
                    'priority': 10,
                    'proxied': False
                },
                {
                    'record_type': 'CNAME',
                    'name': f'mail.{domain}',
                    'content': mail_server,
                    'proxied': False
                }
            ])
        
        return self.bulk_create_records(
            zone_id=zone_id,
            records=records_to_create,
            validate_all=True,
            stop_on_error=False
        )
    
    def _validate_record(
        self,
        record_type: str,
        name: str,
        content: str,
        ttl: int,
        proxied: Optional[bool],
        priority: Optional[int]
    ) -> Dict[str, Any]:
        """Validate DNS record parameters."""
        record_type = record_type.upper()
        
        # Check if record type is supported
        if record_type not in self.RECORD_TYPES:
            return {
                'valid': False,
                'error': f"Unsupported record type: {record_type}"
            }
        
        record_info = self.RECORD_TYPES[record_type]
        
        # Validate TTL
        if not (300 <= ttl <= 86400):
            return {
                'valid': False,
                'error': f"TTL must be between 300 and 86400 seconds"
            }
        
        # Validate proxied setting
        if proxied and not record_info.get('supports_proxy', False):
            return {
                'valid': False,
                'error': f"{record_type} records cannot be proxied"
            }
        
        # Validate priority for MX/SRV records
        if record_info.get('requires_priority', False) and priority is None:
            return {
                'valid': False,
                'error': f"{record_type} records require a priority value"
            }
        
        # Basic content validation
        if not content.strip():
            return {
                'valid': False,
                'error': "Record content cannot be empty"
            }
        
        return {'valid': True}
    
    def _validate_record_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a record configuration dict."""
        required_fields = ['record_type', 'name', 'content']
        
        for field in required_fields:
            if field not in config:
                return {
                    'valid': False,
                    'error': f"Missing required field: {field}"
                }
        
        return self._validate_record(
            record_type=config['record_type'],
            name=config['name'],
            content=config['content'],
            ttl=config.get('ttl', 300),
            proxied=config.get('proxied'),
            priority=config.get('priority')
        )
    
    def _should_proxy_record(self, record_type: str) -> bool:
        """Determine if a record type should be proxied by default."""
        record_type = record_type.upper()
        record_info = self.RECORD_TYPES.get(record_type, {})
        return record_info.get('supports_proxy', False)
