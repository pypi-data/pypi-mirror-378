"""
Flask WSAP Views

Provides Blueprint with WSAP-related views and endpoints.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app, g, abort, render_template_string
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

# Create blueprint
wsap_blueprint = Blueprint('wsap', __name__, url_prefix='/wsap')


# Dashboard template (simple HTML for demo purposes)
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>WSAP Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .info { background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .entity { background: white; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        .verified { border-left: 5px solid #4CAF50; }
        .unverified { border-left: 5px solid #FFC107; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1>WSAP Dashboard</h1>
    <div class="info">
        <h2>Configuration Status</h2>
        <p><strong>API Key:</strong> {{ 'Configured' if has_api_key else 'Not configured' }}</p>
        <p><strong>Base URL:</strong> {{ base_url }}</p>
        <p><strong>Entity ID:</strong> {{ entity_id or 'Not configured' }}</p>
        <p><strong>Auto-serve endpoint:</strong> {{ wsap_endpoint if auto_serve else 'Disabled' }}</p>
    </div>
    
    {% if entities %}
    <h2>Entities</h2>
    {% for entity in entities %}
    <div class="entity {{ 'verified' if entity.domain_verified else 'unverified' }}">
        <h3>{{ entity.name }}</h3>
        <p><strong>ID:</strong> {{ entity.wsap_id }}</p>
        <p><strong>Type:</strong> {{ entity.entity_type }}</p>
        <p><strong>Domain:</strong> {{ entity.primary_domain }}</p>
        <p><strong>Verified:</strong> {{ 'Yes' if entity.domain_verified else 'No' }}</p>
    </div>
    {% endfor %}
    {% else %}
    <p>No entities found.</p>
    {% endif %}
</body>
</html>
'''


@wsap_blueprint.route('/dashboard')
def dashboard():
    """Display WSAP dashboard with configuration and entity information."""
    wsap = current_app.extensions.get('wsap')
    
    if not wsap:
        abort(500, description="WSAP extension not initialized")
    
    # Gather configuration info
    config = current_app.config
    context = {
        'has_api_key': bool(config.get('WSAP_API_KEY')),
        'base_url': config.get('WSAP_BASE_URL', 'https://api.ltfi.ai'),
        'entity_id': config.get('WSAP_ENTITY_ID'),
        'auto_serve': config.get('WSAP_AUTO_SERVE', True),
        'wsap_endpoint': config.get('WSAP_ENDPOINT', '/.well-known/wsap.json'),
        'entities': []
    }
    
    # Try to fetch entities if client is available
    if wsap.client:
        try:
            context['entities'] = wsap.get_entities()
        except Exception as e:
            logger.error(f"Error fetching entities for dashboard: {e}")
    
    return render_template_string(DASHBOARD_TEMPLATE, **context)


@wsap_blueprint.route('/api/entities', methods=['GET'])
def list_entities():
    """
    List all entities.
    
    Query parameters:
    - entity_type: Filter by entity type
    - verified: Filter by verification status (true/false)
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    # Parse query parameters
    filters = {}
    if request.args.get('entity_type'):
        filters['entity_type'] = request.args.get('entity_type')
    if request.args.get('verified'):
        filters['verified'] = request.args.get('verified').lower() == 'true'
    if request.args.get('limit'):
        filters['limit'] = int(request.args.get('limit', 100))
    if request.args.get('offset'):
        filters['offset'] = int(request.args.get('offset', 0))
    
    try:
        entities = wsap.get_entities(**filters)
        return jsonify({
            'entities': entities,
            'count': len(entities),
            'filters': filters
        })
    except Exception as e:
        logger.error(f"Error listing entities: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id: str):
    """Get a specific entity by ID."""
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    try:
        wsap_data = wsap.get_wsap_data(entity_id)
        if not wsap_data:
            return jsonify({'error': 'Entity not found'}), 404
        
        return jsonify(wsap_data)
    except Exception as e:
        logger.error(f"Error fetching entity {entity_id}: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/entities', methods=['POST'])
def create_entity():
    """
    Create a new entity.
    
    Expected JSON body:
    {
        "name": "Entity Name",
        "entity_type": "company",
        "primary_domain": "https://example.com",
        "description": "Entity description",
        ...
    }
    """
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    entity_data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'entity_type', 'primary_domain']
    missing_fields = [field for field in required_fields if field not in entity_data]
    
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400
    
    try:
        created_entity = wsap.create_entity(entity_data)
        return jsonify(created_entity), 201
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/entities/<entity_id>', methods=['PUT', 'PATCH'])
def update_entity(entity_id: str):
    """
    Update an entity.
    
    PUT replaces the entire entity, PATCH updates specific fields.
    """
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    updates = request.get_json()
    
    try:
        updated_entity = wsap.update_entity(entity_id, updates)
        if not updated_entity:
            return jsonify({'error': 'Entity not found'}), 404
        
        return jsonify(updated_entity)
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/entities/<entity_id>', methods=['DELETE'])
def delete_entity(entity_id: str):
    """Delete an entity."""
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    try:
        success = wsap.delete_entity(entity_id)
        if not success:
            return jsonify({'error': 'Entity not found'}), 404
        
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/verify-domain', methods=['POST'])
def verify_domain():
    """
    Verify domain ownership.
    
    Expected JSON body:
    {
        "domain": "example.com"
    }
    """
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    domain = data.get('domain')
    
    if not domain:
        return jsonify({'error': 'Domain is required'}), 400
    
    try:
        verified = wsap.verify_domain(domain)
        return jsonify({
            'domain': domain,
            'verified': verified,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error verifying domain {domain}: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/api/generate', methods=['POST'])
def generate_wsap():
    """
    Generate WSAP JSON for an entity.
    
    Expected JSON body:
    {
        "entity_id": "entity-123",
        "disclosure_level": "standard"  // optional: basic, standard, detailed, complete
    }
    """
    wsap = current_app.extensions.get('wsap')
    
    if not wsap or not wsap.client:
        return jsonify({'error': 'WSAP not configured'}), 503
    
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    entity_id = data.get('entity_id')
    
    if not entity_id:
        return jsonify({'error': 'entity_id is required'}), 400
    
    try:
        wsap_data = wsap.get_wsap_data(entity_id)
        if not wsap_data:
            return jsonify({'error': 'Entity not found'}), 404
        
        # Apply disclosure level if specified
        disclosure_level = data.get('disclosure_level', 'standard')
        if disclosure_level in ['basic', 'minimal']:
            # Filter out detailed fields for basic disclosure
            filtered_data = {
                'wsap_version': wsap_data.get('wsap_version'),
                'entity': {
                    'name': wsap_data.get('entity', {}).get('name'),
                    'type': wsap_data.get('entity', {}).get('type'),
                    'primary_domain': wsap_data.get('entity', {}).get('primary_domain')
                },
                '_metadata': wsap_data.get('_metadata')
            }
            return jsonify(filtered_data)
        
        return jsonify(wsap_data)
        
    except Exception as e:
        logger.error(f"Error generating WSAP for entity {entity_id}: {e}")
        return jsonify({'error': str(e)}), 500


@wsap_blueprint.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    wsap = current_app.extensions.get('wsap')
    
    status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'wsap_configured': bool(wsap),
        'client_available': bool(wsap and wsap.client)
    }
    
    # Check if we can connect to WSAP API
    if wsap and wsap.client:
        try:
            # Try a simple API call
            wsap.client.list_entities(limit=1)
            status['api_reachable'] = True
        except Exception:
            status['api_reachable'] = False
            status['status'] = 'degraded'
    
    return jsonify(status)


# Error handlers for the blueprint
@wsap_blueprint.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': str(error.description) if hasattr(error, 'description') else 'Resource not found'
    }), 404


@wsap_blueprint.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
