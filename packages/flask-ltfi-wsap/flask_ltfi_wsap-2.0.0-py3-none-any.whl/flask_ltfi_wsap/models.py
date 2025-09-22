"""
Flask WSAP Models

Provides data models and schemas for WSAP entities.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import json


class EntityType(Enum):
    """Supported entity types in WSAP."""
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    PERSONAL = "personal_brand"
    OPENSOURCE = "open_source"
    AI_AGENT = "ai_agent"
    OTHER = "other"


class DisclosureLevel(Enum):
    """Progressive disclosure levels."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPLETE = "complete"


class WSAPEntity:
    """
    Represents a WSAP entity.
    
    This is a simple model class for Flask applications that don't use an ORM.
    For SQLAlchemy integration, see the flask-sqlalchemy-wsap package.
    """
    
    def __init__(self, **kwargs):
        """Initialize entity with provided attributes."""
        self.wsap_id = kwargs.get('wsap_id')
        self.name = kwargs.get('name')
        self.entity_type = kwargs.get('entity_type', EntityType.COMPANY.value)
        self.primary_domain = kwargs.get('primary_domain')
        self.domains = kwargs.get('domains', [])
        self.description = kwargs.get('description')
        self.logo_url = kwargs.get('logo_url')
        self.domain_verified = kwargs.get('domain_verified', False)
        self.verification_token = kwargs.get('verification_token')
        self.verified_at = kwargs.get('verified_at')
        self.disclosure_level = kwargs.get('disclosure_level', DisclosureLevel.STANDARD.value)
        
        # Contact information
        self.contact_email = kwargs.get('contact_email')
        self.contact_phone = kwargs.get('contact_phone')
        self.contact_address = kwargs.get('contact_address')
        
        # Social profiles
        self.social_profiles = kwargs.get('social_profiles', {})
        
        # Business information
        self.industry = kwargs.get('industry')
        self.size = kwargs.get('size')
        self.founded = kwargs.get('founded')
        self.headquarters = kwargs.get('headquarters')
        
        # Legal and compliance
        self.legal_name = kwargs.get('legal_name')
        self.registration_number = kwargs.get('registration_number')
        self.tax_id = kwargs.get('tax_id')
        self.licenses = kwargs.get('licenses', [])
        
        # Technical capabilities
        self.api_endpoints = kwargs.get('api_endpoints', [])
        self.supported_protocols = kwargs.get('supported_protocols', [])
        self.security_measures = kwargs.get('security_measures', [])
        
        # Metadata
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.metadata = kwargs.get('metadata', {})
    
    def to_dict(self, disclosure_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert entity to dictionary representation.
        
        Args:
            disclosure_level: Optional disclosure level to apply
            
        Returns:
            Dictionary representation of the entity
        """
        disclosure_level = disclosure_level or self.disclosure_level
        
        # Basic information (always included)
        data = {
            'wsap_id': self.wsap_id,
            'name': self.name,
            'entity_type': self.entity_type,
            'primary_domain': self.primary_domain,
            'domain_verified': self.domain_verified
        }
        
        # Standard level includes more details
        if disclosure_level in [DisclosureLevel.STANDARD.value, 
                                DisclosureLevel.DETAILED.value,
                                DisclosureLevel.COMPLETE.value]:
            data.update({
                'description': self.description,
                'logo_url': self.logo_url,
                'domains': self.domains,
                'contact_email': self.contact_email,
                'industry': self.industry,
                'size': self.size,
                'social_profiles': self.social_profiles
            })
        
        # Detailed level includes business information
        if disclosure_level in [DisclosureLevel.DETAILED.value,
                                DisclosureLevel.COMPLETE.value]:
            data.update({
                'contact_phone': self.contact_phone,
                'contact_address': self.contact_address,
                'founded': self.founded,
                'headquarters': self.headquarters,
                'legal_name': self.legal_name,
                'api_endpoints': self.api_endpoints,
                'supported_protocols': self.supported_protocols
            })
        
        # Complete level includes everything
        if disclosure_level == DisclosureLevel.COMPLETE.value:
            data.update({
                'registration_number': self.registration_number,
                'tax_id': self.tax_id,
                'licenses': self.licenses,
                'security_measures': self.security_measures,
                'verified_at': self.verified_at.isoformat() if self.verified_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'metadata': self.metadata
            })
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def to_wsap_json(self, disclosure_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate WSAP-compliant JSON representation.
        
        Args:
            disclosure_level: Optional disclosure level to apply
            
        Returns:
            WSAP-compliant JSON structure
        """
        entity_data = self.to_dict(disclosure_level)
        
        wsap_json = {
            'wsap_version': '2.0',
            'entity': entity_data,
            'verification': {
                'domain_verified': self.domain_verified,
                'verified_at': self.verified_at.isoformat() if self.verified_at else None,
                'verification_method': 'DNS_TXT'
            },
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'disclosure_level': disclosure_level or self.disclosure_level,
                'source': 'flask-ltfi-wsap'
            }
        }
        
        # Add protocol information if available
        if self.supported_protocols:
            wsap_json['protocols'] = {
                'supported': self.supported_protocols,
                'version': '2.0'
            }
        
        # Add API information if available
        if self.api_endpoints:
            wsap_json['api'] = {
                'endpoints': self.api_endpoints,
                'authentication': 'Bearer token',
                'rate_limiting': 'Standard'
            }
        
        return wsap_json
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WSAPEntity':
        """
        Create entity from dictionary.
        
        Args:
            data: Dictionary containing entity data
            
        Returns:
            WSAPEntity instance
        """
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        if 'verified_at' in data and isinstance(data['verified_at'], str):
            data['verified_at'] = datetime.fromisoformat(data['verified_at'].replace('Z', '+00:00'))
        
        return cls(**data)
    
    def __repr__(self):
        """String representation of the entity."""
        return f"<WSAPEntity {self.wsap_id}: {self.name}>)"


class WSAPValidator:
    """
    Validator for WSAP data structures.
    """
    
    @staticmethod
    def validate_entity(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate entity data.
        
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
        if 'entity_type' in data:
            valid_types = [e.value for e in EntityType]
            if data['entity_type'] not in valid_types:
                errors.append(f"Invalid entity_type: {data['entity_type']}. Must be one of: {valid_types}")
        
        # Validate disclosure level if present
        if 'disclosure_level' in data:
            valid_levels = [e.value for e in DisclosureLevel]
            if data['disclosure_level'] not in valid_levels:
                errors.append(f"Invalid disclosure_level: {data['disclosure_level']}. Must be one of: {valid_levels}")
        
        # Validate domain format
        if 'primary_domain' in data:
            domain = data['primary_domain']
            if not domain.startswith(('http://', 'https://')):
                errors.append(f"Primary domain must include protocol (http:// or https://)")
        
        # Validate email format
        if 'contact_email' in data and data['contact_email']:
            email = data['contact_email']
            if '@' not in email or '.' not in email.split('@')[1]:
                errors.append(f"Invalid email format: {email}")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def validate_wsap_json(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate WSAP JSON structure.
        
        Args:
            data: WSAP JSON data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level fields
        if 'wsap_version' not in data:
            errors.append("Missing required field 'wsap_version'")
        elif data['wsap_version'] not in ['1.0', '2.0']:
            errors.append(f"Unsupported WSAP version: {data['wsap_version']}")
        
        if 'entity' not in data:
            errors.append("Missing required field 'entity'")
        elif isinstance(data['entity'], dict):
            # Validate entity data
            is_valid, entity_errors = WSAPValidator.validate_entity(data['entity'])
            errors.extend(entity_errors)
        else:
            errors.append("Field 'entity' must be a dictionary")
        
        # Validate optional sections if present
        if 'verification' in data and not isinstance(data['verification'], dict):
            errors.append("Field 'verification' must be a dictionary")
        
        if 'metadata' in data and not isinstance(data['metadata'], dict):
            errors.append("Field 'metadata' must be a dictionary")
        
        return (len(errors) == 0, errors)


class WSAPSchema:
    """
    Schema definitions for WSAP data.
    """
    
    @staticmethod
    def get_entity_schema() -> Dict[str, Any]:
        """Get JSON schema for WSAP entity."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["name", "entity_type", "primary_domain"],
            "properties": {
                "wsap_id": {"type": "string"},
                "name": {"type": "string"},
                "entity_type": {
                    "type": "string",
                    "enum": [e.value for e in EntityType]
                },
                "primary_domain": {
                    "type": "string",
                    "format": "uri"
                },
                "domains": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"}
                },
                "description": {"type": "string"},
                "logo_url": {"type": "string", "format": "uri"},
                "domain_verified": {"type": "boolean"},
                "disclosure_level": {
                    "type": "string",
                    "enum": [e.value for e in DisclosureLevel]
                },
                "contact_email": {"type": "string", "format": "email"},
                "contact_phone": {"type": "string"},
                "contact_address": {"type": "string"},
                "social_profiles": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "industry": {"type": "string"},
                "size": {"type": "string"},
                "founded": {"type": "string"},
                "headquarters": {"type": "string"},
                "legal_name": {"type": "string"},
                "registration_number": {"type": "string"},
                "tax_id": {"type": "string"},
                "licenses": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "api_endpoints": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "supported_protocols": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "security_measures": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    
    @staticmethod
    def get_wsap_schema() -> Dict[str, Any]:
        """Get JSON schema for WSAP document."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["wsap_version", "entity"],
            "properties": {
                "wsap_version": {
                    "type": "string",
                    "enum": ["1.0", "2.0"]
                },
                "entity": WSAPSchema.get_entity_schema(),
                "verification": {
                    "type": "object",
                    "properties": {
                        "domain_verified": {"type": "boolean"},
                        "verified_at": {"type": "string", "format": "date-time"},
                        "verification_method": {"type": "string"}
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "generated_at": {"type": "string", "format": "date-time"},
                        "disclosure_level": {"type": "string"},
                        "source": {"type": "string"}
                    }
                },
                "protocols": {
                    "type": "object",
                    "properties": {
                        "supported": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "version": {"type": "string"}
                    }
                },
                "api": {
                    "type": "object",
                    "properties": {
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "authentication": {"type": "string"},
                        "rate_limiting": {"type": "string"}
                    }
                }
            }
        }
