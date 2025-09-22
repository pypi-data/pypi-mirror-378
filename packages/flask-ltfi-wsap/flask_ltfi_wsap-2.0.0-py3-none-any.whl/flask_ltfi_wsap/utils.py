"""
Flask WSAP Utilities

Helper functions and utilities for WSAP integration.
"""

import json
import logging
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlparse
import dns.resolver
from functools import wraps
from flask import request, jsonify, current_app

logger = logging.getLogger(__name__)


def generate_verification_token(domain: str, secret_key: str) -> str:
    """
    Generate a verification token for domain ownership.
    
    Args:
        domain: Domain to generate token for
        secret_key: Secret key for HMAC
        
    Returns:
        Verification token string
    """
    message = f"wsap-verify:{domain}:{datetime.utcnow().date().isoformat()}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    
    token = base64.b64encode(signature).decode('utf-8')
    return f"wsap-site-verification={token[:32]}"


def verify_dns_txt_record(domain: str, expected_token: str) -> bool:
    """
    Verify domain ownership via DNS TXT record.
    
    Args:
        domain: Domain to verify
        expected_token: Expected verification token
        
    Returns:
        True if verified, False otherwise
    """
    try:
        # Remove protocol if present
        parsed = urlparse(domain)
        domain_name = parsed.netloc or parsed.path
        
        # Query DNS TXT records
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5.0
        resolver.lifetime = 10.0
        
        answers = resolver.resolve(domain_name, 'TXT')
        
        for rdata in answers:
            for txt_string in rdata.strings:
                txt_value = txt_string.decode('utf-8')
                if expected_token in txt_value:
                    logger.info(f"Domain {domain_name} verified successfully")
                    return True
        
        logger.warning(f"Domain {domain_name} verification failed: token not found")
        return False
        
    except Exception as e:
        logger.error(f"DNS verification error for {domain}: {e}")
        return False


def sanitize_domain(domain: str) -> str:
    """
    Sanitize and validate domain URL.
    
    Args:
        domain: Domain URL to sanitize
        
    Returns:
        Sanitized domain URL
    """
    if not domain:
        raise ValueError("Domain cannot be empty")
    
    # Add protocol if missing
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    
    # Parse and validate
    parsed = urlparse(domain)
    if not parsed.netloc:
        raise ValueError(f"Invalid domain: {domain}")
    
    # Reconstruct clean URL
    return f"{parsed.scheme}://{parsed.netloc}"


def rate_limit(max_calls: int = 60, time_window: int = 60):
    """
    Rate limiting decorator for Flask routes.
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
        
    Returns:
        Decorated function
    """
    def decorator(f):
        call_times = {}
        
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.remote_addr
            
            now = datetime.utcnow()
            
            # Clean old entries
            cutoff = now - timedelta(seconds=time_window)
            if client_id in call_times:
                call_times[client_id] = [
                    t for t in call_times[client_id] if t > cutoff
                ]
            
            # Check rate limit
            if client_id in call_times:
                if len(call_times[client_id]) >= max_calls:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': time_window
                    }), 429
            
            # Record this call
            if client_id not in call_times:
                call_times[client_id] = []
            call_times[client_id].append(now)
            
            return f(*args, **kwargs)
        
        return wrapped
    return decorator


def cache_result(timeout: int = 300):
    """
    Simple caching decorator for Flask functions.
    
    Args:
        timeout: Cache timeout in seconds
        
    Returns:
        Decorated function
    """
    def decorator(f):
        cache = {}
        
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Create cache key
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            if cache_key in cache:
                cached_value, cached_time = cache[cache_key]
                if datetime.utcnow() - cached_time < timedelta(seconds=timeout):
                    return cached_value
            
            # Call function and cache result
            result = f(*args, **kwargs)
            cache[cache_key] = (result, datetime.utcnow())
            
            return result
        
        return wrapped
    return decorator


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    # Check format (e.g., wsap_xxx... format)
    if not api_key.startswith('wsap_'):
        return False
    
    # Check length (should be at least 32 characters)
    if len(api_key) < 32:
        return False
    
    # Additional validation could be added here
    return True


def format_wsap_response(
    data: Any,
    success: bool = True,
    message: Optional[str] = None,
    errors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Format a standardized WSAP API response.
    
    Args:
        data: Response data
        success: Whether the operation was successful
        message: Optional message
        errors: Optional list of errors
        
    Returns:
        Formatted response dictionary
    """
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = errors
    
    return response


def encrypt_sensitive_field(value: str, key: bytes) -> str:
    """
    Encrypt sensitive field using AES-256-GCM.
    
    Args:
        value: Value to encrypt
        key: Encryption key
        
    Returns:
        Encrypted value as base64 string
    """
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    import os
    
    # Generate nonce
    nonce = os.urandom(12)
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    )
    
    # Encrypt
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(value.encode()) + encryptor.finalize()
    
    # Combine nonce, tag, and ciphertext
    encrypted = nonce + encryptor.tag + ciphertext
    
    # Return as base64
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_sensitive_field(encrypted_value: str, key: bytes) -> str:
    """
    Decrypt sensitive field encrypted with AES-256-GCM.
    
    Args:
        encrypted_value: Base64 encoded encrypted value
        key: Decryption key
        
    Returns:
        Decrypted value
    """
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    
    # Decode from base64
    encrypted = base64.b64decode(encrypted_value)
    
    # Extract components
    nonce = encrypted[:12]
    tag = encrypted[12:28]
    ciphertext = encrypted[28:]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )
    
    # Decrypt
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    return plaintext.decode('utf-8')


def parse_disclosure_level(request_headers: dict) -> str:
    """
    Parse disclosure level from request headers.
    
    Args:
        request_headers: Request headers dictionary
        
    Returns:
        Disclosure level string
    """
    # Check for disclosure level header
    disclosure = request_headers.get('X-WSAP-Disclosure-Level', '').lower()
    
    valid_levels = ['basic', 'standard', 'detailed', 'complete']
    
    if disclosure in valid_levels:
        return disclosure
    
    # Default to standard
    return 'standard'


def validate_entity_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate entity data structure.
    
    Args:
        data: Entity data to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = ['name', 'entity_type', 'primary_domain']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Required field '{field}' is missing or empty")
    
    # Validate entity type
    valid_types = ['company', 'nonprofit', 'government', 'personal_brand', 'open_source', 'ai_agent', 'other']
    if 'entity_type' in data and data['entity_type'] not in valid_types:
        errors.append(f"Invalid entity_type: {data['entity_type']}")
    
    # Validate domain format
    if 'primary_domain' in data:
        try:
            sanitize_domain(data['primary_domain'])
        except ValueError as e:
            errors.append(str(e))
    
    # Validate email if present
    if 'contact_email' in data and data['contact_email']:
        email = data['contact_email']
        if '@' not in email or '.' not in email.split('@')[1]:
            errors.append(f"Invalid email format: {email}")
    
    return (len(errors) == 0, errors)


def get_client_ip(request) -> str:
    """
    Get the real client IP address from request.
    
    Args:
        request: Flask request object
        
    Returns:
        Client IP address
    """
    # Check for proxy headers
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    
    return ip


def log_api_request(endpoint: str, method: str, client_ip: str, data: Optional[Dict] = None):
    """
    Log API request for auditing.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        client_ip: Client IP address
        data: Optional request data
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'client_ip': client_ip
    }
    
    if data:
        # Remove sensitive fields
        safe_data = {k: v for k, v in data.items() 
                    if k not in ['password', 'api_key', 'secret', 'token']}
        log_entry['data'] = safe_data
    
    logger.info(f"API Request: {json.dumps(log_entry)}")


def merge_wsap_data(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge WSAP data dictionaries.
    
    Args:
        base: Base dictionary
        updates: Updates to apply
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_wsap_data(result[key], value)
        elif value is not None:
            # Update or add the value
            result[key] = value
    
    return result