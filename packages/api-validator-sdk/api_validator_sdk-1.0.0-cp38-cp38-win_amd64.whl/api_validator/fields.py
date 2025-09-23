"""
Predefined field configurations for common API validation scenarios
"""

from typing import List
from .core import Field

# Authentication Fields
AUTH_FIELDS = [
    Field('auth_token_present', True, 5.0, 5.0),
    Field('auth_token_valid_length', True, 5.0, 5.0),
    Field('token_age_minutes', 15, 4.0, 3.5),
    Field('user_verified', True, 5.0, 5.0),
    Field('user_id', True, 4.0, 5.0),
    Field('session_valid', True, 4.0, 4.0),
]

# Rate Limiting Fields
RATE_LIMIT_FIELDS = [
    Field('requests_per_minute', 30, 4.0, 4.0),
    Field('requests_per_hour', 1000, 3.5, 3.0),
    Field('daily_requests', 5000, 3.0, 2.5),
    Field('concurrent_connections', 10, 3.0, 3.0),
    Field('bandwidth_mb_per_minute', 100, 2.5, 2.0),
]

# Security Fields
SECURITY_FIELDS = [
    Field('ip_reputation_score', 75, 4.0, 3.0),
    Field('failed_attempts', 0, 3.5, 3.0),
    Field('geo_restricted', False, 3.0, 4.0),
    Field('known_attacker_signature', False, 5.0, 5.0),
    Field('suspicious_patterns', False, 4.0, 4.0),
    Field('account_age_days', 30, 2.0, 1.5),
    Field('user_agent_suspicious', False, 2.0, 2.0),
]

# Payload Validation Fields
PAYLOAD_FIELDS = [
    Field('payload_size_kb', 1024, 3.0, 2.5),
    Field('content_type', 'application/json', 2.0, 3.0),
    Field('has_required_fields', True, 4.0, 5.0),
    Field('json_valid', True, 4.0, 5.0),
    Field('encoding', 'utf-8', 2.0, 3.0),
]

# Permission Fields
PERMISSION_FIELDS = [
    Field('user_role', 'user', 3.0, 2.0),
    Field('resource_owner', True, 4.0, 4.0),
    Field('admin_endpoint', False, 5.0, 5.0),
    Field('write_permission', False, 3.0, 3.0),
    Field('delete_permission', False, 4.0, 4.0),
]

# Business Logic Fields
BUSINESS_FIELDS = [
    Field('user_plan', 'pro', 2.0, 2.0),
    Field('within_quota', True, 3.0, 3.0),
    Field('payment_current', True, 4.0, 5.0),
    Field('terms_accepted', True, 5.0, 5.0),
    Field('gdpr_consent', True, 4.0, 5.0),
]

def get_standard_fields() -> List[Field]:
    """Get all standard fields for comprehensive validation"""
    return (AUTH_FIELDS + RATE_LIMIT_FIELDS + SECURITY_FIELDS + 
            PAYLOAD_FIELDS[:3])  # Only essential payload fields

def get_strict_security_fields() -> List[Field]:
    """Get fields for strict security validation"""
    strict_fields = AUTH_FIELDS + SECURITY_FIELDS
    # Increase importance and sensitivity for strict mode
    for field in strict_fields:
        field.importance *= 1.5
        field.sensitivity *= 1.5
    return strict_fields

def get_minimal_fields() -> List[Field]:
    """Get minimal set of fields for basic validation"""
    return [
        Field('auth_token_present', True, 5.0, 5.0),
        Field('user_verified', True, 4.0, 4.0),
        Field('requests_per_minute', 100, 3.0, 2.0),
        Field('payload_size_kb', 5000, 2.0, 1.5),
    ]

def create_custom_field(name: str, reference: any, 
                       importance: float = 2.0, 
                       sensitivity: float = 2.0) -> Field:
    """Helper to create custom field with defaults"""
    return Field(name, reference, importance, sensitivity)

# Preset configurations for common scenarios
class FieldPresets:
    @staticmethod
    def public_api() -> List[Field]:
        """Fields for public API endpoints"""
        return [
            Field('rate_limit_exceeded', False, 5.0, 5.0),
            Field('requests_per_minute', 10, 4.0, 4.0),
            Field('ip_reputation_score', 50, 3.0, 2.5),
            Field('payload_size_kb', 512, 3.0, 2.0),
        ]
    
    @staticmethod
    def internal_api() -> List[Field]:
        """Fields for internal API endpoints"""
        return [
            Field('internal_token_valid', True, 5.0, 5.0),
            Field('service_name', 'known_service', 4.0, 4.0),
            Field('vpc_origin', True, 4.0, 5.0),
        ]
    
    @staticmethod
    def webhook() -> List[Field]:
        """Fields for webhook validation"""
        return [
            Field('signature_valid', True, 5.0, 5.0),
            Field('timestamp_fresh', True, 4.0, 4.0),
            Field('retry_count', 0, 2.0, 1.5),
            Field('webhook_registered', True, 5.0, 5.0),
        ]
    
    @staticmethod
    def graphql() -> List[Field]:
        """Fields for GraphQL endpoint validation"""
        return [
            Field('query_complexity', 100, 4.0, 3.5),
            Field('query_depth', 5, 3.5, 3.0),
            Field('mutation_allowed', False, 3.0, 4.0),
            Field('introspection_allowed', False, 2.0, 3.0),
        ]