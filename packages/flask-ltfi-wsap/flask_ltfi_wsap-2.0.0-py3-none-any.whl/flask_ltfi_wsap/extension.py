"""
Flask WSAP Extension

Provides Flask application integration for LTFI-WSAP protocol.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, current_app, g, abort
from werkzeug.exceptions import HTTPException

try:
    from ltfi_wsap import WSAPClient
except ImportError:
    WSAPClient = None

logger = logging.getLogger(__name__)


class WSAPError(Exception):
    """Base exception for WSAP-related errors."""
    pass


class WSAP:
    """
    Flask extension for LTFI-WSAP integration.
    
    Usage:
        app = Flask(__name__)
        wsap = WSAP(app)
        
    Or with factory pattern:
        wsap = WSAP()
        wsap.init_app(app)
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize the WSAP extension."""
        self.app = app
        self.client: Optional['WSAPClient'] = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the Flask application for use with WSAP."""
        # Configuration defaults
        app.config.setdefault('WSAP_API_KEY', None)
        app.config.setdefault('WSAP_BASE_URL', 'https://api.ltfi.ai')
        app.config.setdefault('WSAP_ENTITY_ID', None)
        app.config.setdefault('WSAP_CACHE_TIMEOUT', 300)  # 5 minutes
        app.config.setdefault('WSAP_AUTO_SERVE', True)
        app.config.setdefault('WSAP_ENDPOINT', '/.well-known/wsap.json')
        app.config.setdefault('WSAP_VERIFY_DOMAINS', True)
        app.config.setdefault('WSAP_LOG_REQUESTS', False)
        
        # Validate required configuration
        if not app.config.get('WSAP_API_KEY'):
            logger.warning("WSAP_API_KEY not configured. WSAP features will be limited.")
        
        # Initialize client if SDK is available
        if WSAPClient and app.config['WSAP_API_KEY']:
            self.client = WSAPClient(
                api_key=app.config['WSAP_API_KEY'],
                base_url=app.config['WSAP_BASE_URL'],
                entity_id=app.config['WSAP_ENTITY_ID']
            )
        
        # Register error handlers
        app.register_error_handler(WSAPError, self._handle_wsap_error)
        
        # Store reference to self in app extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['wsap'] = self
        
        # Register before_request handler
        app.before_request(self._before_request)
        
        # Auto-serve WSAP endpoint if enabled
        if app.config['WSAP_AUTO_SERVE']:
            self._register_wsap_endpoint(app)
    
    def _before_request(self):
        """Before request handler to inject WSAP context."""
        g.wsap = self
        
        # Log requests if enabled
        if current_app.config.get('WSAP_LOG_REQUESTS'):
            logger.debug(f"WSAP Request: {request.method} {request.path}")
    
    def _register_wsap_endpoint(self, app: Flask):
        """Register the WSAP JSON endpoint."""
        endpoint_path = app.config['WSAP_ENDPOINT']
        
        @app.route(endpoint_path, methods=['GET'])
        def serve_wsap_json():
            """Serve the WSAP JSON file."""
            try:
                wsap_data = self.get_wsap_data()
                if not wsap_data:
                    abort(404, description="WSAP data not available")
                
                response = jsonify(wsap_data)
                response.headers['Cache-Control'] = f"public, max-age={app.config['WSAP_CACHE_TIMEOUT']}"
                response.headers['Content-Type'] = 'application/json'
                
                return response
                
            except WSAPError as e:
                logger.error(f"Error serving WSAP data: {e}")
                abort(500, description="Error generating WSAP data")
    
    def _handle_wsap_error(self, error: WSAPError):
        """Handle WSAP-specific errors."""
        logger.error(f"WSAP Error: {error}")
        response = jsonify({
            'error': 'WSAP Error',
            'message': str(error)
        })
        response.status_code = 500
        return response
    
    def get_wsap_data(self, entity_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get WSAP data for the entity.
        
        Args:
            entity_id: Optional entity ID to fetch data for
            
        Returns:
            WSAP data dictionary or None if not available
        """
        if not self.client:
            logger.warning("WSAP client not initialized")
            return None
        
        try:
            entity_id = entity_id or current_app.config.get('WSAP_ENTITY_ID')
            if not entity_id:
                raise WSAPError("No entity ID configured or provided")
            
            # Fetch from API
            wsap_data = self.client.get_entity(entity_id)
            
            # Add metadata
            wsap_data['_metadata'] = {
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'flask-ltfi-wsap',
                'version': '2.0.0'
            }
            
            return wsap_data
            
        except Exception as e:
            logger.error(f"Error fetching WSAP data: {e}")
            raise WSAPError(f"Failed to fetch WSAP data: {e}")
    
    def verify_domain(self, domain: str) -> bool:
        """
        Verify domain ownership through DNS TXT records.
        
        Args:
            domain: Domain to verify
            
        Returns:
            True if verified, False otherwise
        """
        if not self.client:
            raise WSAPError("WSAP client not initialized")
        
        try:
            return self.client.verify_domain(domain)
        except Exception as e:
            logger.error(f"Domain verification failed: {e}")
            return False
    
    def require_wsap(self, f):
        """
        Decorator to require WSAP authentication.
        
        Usage:
            @app.route('/api/protected')
            @wsap.require_wsap
            def protected_route():
                return jsonify({'message': 'WSAP authenticated'})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for WSAP token in headers
            wsap_token = request.headers.get('X-WSAP-Token')
            
            if not wsap_token:
                abort(401, description="WSAP authentication required")
            
            # Validate token with WSAP API
            if not self.validate_token(wsap_token):
                abort(401, description="Invalid WSAP token")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a WSAP token.
        
        Args:
            token: WSAP token to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.client:
            return False
        
        try:
            return self.client.validate_token(token)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False
    
    def get_entities(self, **filters) -> List[Dict[str, Any]]:
        """
        Get list of entities with optional filters.
        
        Args:
            **filters: Optional filters (entity_type, verified, etc.)
            
        Returns:
            List of entity dictionaries
        """
        if not self.client:
            return []
        
        try:
            return self.client.list_entities(**filters)
        except Exception as e:
            logger.error(f"Error fetching entities: {e}")
            return []
    
    def create_entity(self, entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new entity.
        
        Args:
            entity_data: Entity data dictionary
            
        Returns:
            Created entity data or None
        """
        if not self.client:
            raise WSAPError("WSAP client not initialized")
        
        try:
            return self.client.create_entity(entity_data)
        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            raise WSAPError(f"Failed to create entity: {e}")
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an entity.
        
        Args:
            entity_id: Entity ID to update
            updates: Update data dictionary
            
        Returns:
            Updated entity data or None
        """
        if not self.client:
            raise WSAPError("WSAP client not initialized")
        
        try:
            return self.client.update_entity(entity_id, updates)
        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            raise WSAPError(f"Failed to update entity: {e}")
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: Entity ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.client:
            raise WSAPError("WSAP client not initialized")
        
        try:
            return self.client.delete_entity(entity_id)
        except Exception as e:
            logger.error(f"Error deleting entity: {e}")
            return False
