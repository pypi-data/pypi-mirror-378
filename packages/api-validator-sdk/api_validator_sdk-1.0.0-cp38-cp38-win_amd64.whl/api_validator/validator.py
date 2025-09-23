"""
Main API Validator class with commercial licensing and enterprise features
"""

from typing import Dict, List, Tuple, Optional, Union
from .core import Field, AdaptiveFormula
from .fields import get_standard_fields
from .models import ValidationResult, RequestMetrics

class APIValidator:
    """
    Enterprise-grade API request validator with intelligent scoring and licensing
    """
    
    def __init__(self, custom_fields: List[Field] = None, 
                 use_standard_fields: bool = True,
                 confidence_level: float = 0.65,
                 tier: str = 'community',
                 license_key: str = None):
        """
        Initialize API Validator with commercial features
        
        Args:
            custom_fields: Additional custom validation fields
            use_standard_fields: Include standard auth/rate/security fields
            confidence_level: Initial confidence threshold (0-1)
            tier: License tier ('community', 'professional', 'enterprise')
            license_key: License key for premium features
        """
        self.tier = tier
        self.license_key = license_key
        self.fields = []
        
        if use_standard_fields:
            self.fields.extend(get_standard_fields())
        
        if custom_fields:
            self.fields.extend(custom_fields)
        
        self._setup_formula(confidence_level)
        
    def _setup_formula(self, confidence_level: float):
        """Setup the adaptive formula with configured fields and licensing"""
        config = {field.name: field.to_dict() for field in self.fields}
        self.formula = AdaptiveFormula(config, tier=self.tier, license_key=self.license_key)
        self.formula.set_confidence_level(confidence_level)
    
    def validate_request(self, request: Union[Dict, any]) -> ValidationResult:
        """
        Validate a complete API request with tier-specific features
        
        Args:
            request: Dictionary containing request data (or DataFrame/Series for Pro/Enterprise)
            
        Returns:
            ValidationResult with score, decision, and details
        """
        # Process heterogeneous data for Pro/Enterprise tiers
        if self.tier != 'community':
            try:
                request = self.formula.process_heterogeneous(request)
            except ValueError:
                pass  # Keep as-is if already dict
        
        score = self.formula.evaluate(request)
        threshold = self.formula.get_confidence_level()
        is_valid = score > threshold
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            threshold=threshold,
            message=self._get_validation_message(score, threshold),
            details=self._analyze_validation(request, score)
        )
    
    def validate_batch(self, requests: List[Dict]) -> List[ValidationResult]:
        """
        Batch validation for multiple requests (Professional/Enterprise feature)
        
        Args:
            requests: List of request dictionaries
            
        Returns:
            List of ValidationResults
        """
        if self.tier == 'community':
            raise ValueError("Batch validation requires Professional or Enterprise license")
        
        results = []
        for request in requests:
            results.append(self.validate_request(request))
        
        return results
    
    def validate_dataframe(self, df):
        """
        Validate pandas DataFrame rows (Professional/Enterprise feature)
        
        Args:
            df: pandas DataFrame with request data
            
        Returns:
            List of ValidationResults
        """
        if self.tier == 'community':
            raise ValueError("DataFrame support requires Professional or Enterprise license")
        
        try:
            import pandas as pd
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")
        except ImportError:
            raise ImportError("pandas is required for DataFrame support")
        
        results = []
        for idx, row in df.iterrows():
            result = self.validate_request(row)
            results.append(result)
        
        return results
    
    def check_auth(self, token_data: Dict[str, any]) -> Tuple[bool, float]:
        """
        Specialized authentication check
        
        Args:
            token_data: Dict with token info
            
        Returns:
            (is_authenticated, confidence_score)
        """
        auth_fields = [
            Field('token_present', True, 5.0, 5.0),
            Field('token_age_minutes', 15, 4.0, 3.5),
            Field('user_verified', True, 4.0, 4.0)
        ]
        
        config = {field.name: field.to_dict() for field in auth_fields}
        auth_formula = AdaptiveFormula(config, tier=self.tier, license_key=self.license_key)
        
        score = auth_formula.evaluate(token_data)
        return score > 0.7, score
    
    def check_rate_limit(self, usage_data: Dict[str, any]) -> Tuple[bool, float]:
        """
        Check if request is within rate limits with adaptive thresholds
        
        Args:
            usage_data: Dict with usage metrics
            
        Returns:
            (within_limits, score)
        """
        rate_fields = [
            Field('requests_per_minute', 30, 4.0, 4.0),
            Field('requests_per_hour', 1000, 3.5, 3.0),
            Field('daily_requests', 5000, 3.0, 2.5)
        ]
        
        config = {field.name: field.to_dict() for field in rate_fields}
        rate_formula = AdaptiveFormula(config, tier=self.tier, license_key=self.license_key)
        
        score = rate_formula.evaluate(usage_data)
        # Pro/Enterprise: Use adaptive threshold
        threshold = rate_formula.get_confidence_level() if self.tier != 'community' else 0.6
        
        return score > threshold, score
    
    def validate_payload(self, payload_data: Dict[str, any]) -> Tuple[bool, float]:
        """
        Validate request payload
        
        Args:
            payload_data: Dict with payload info
            
        Returns:
            (is_valid, score)
        """
        payload_fields = [
            Field('payload_size_kb', 1024, 3.0, 2.5),
            Field('content_type', 'application/json', 2.0, 3.0),
            Field('has_required_fields', True, 4.0, 5.0)
        ]
        
        config = {field.name: field.to_dict() for field in payload_fields}
        payload_formula = AdaptiveFormula(config, tier=self.tier, license_key=self.license_key)
        
        score = payload_formula.evaluate(payload_data)
        return score > 0.65, score
    
    def check_permissions(self, user_role: str, endpoint: str, 
                         method: str = 'GET') -> Tuple[bool, str]:
        """
        Check if user has permission for endpoint
        
        Args:
            user_role: User's role
            endpoint: API endpoint path
            method: HTTP method
            
        Returns:
            (has_permission, message)
        """
        permission_map = {
            'admin': {'GET': '*', 'POST': '*', 'PUT': '*', 'DELETE': '*'},
            'editor': {'GET': '*', 'POST': '*', 'PUT': '*', 'DELETE': 'restricted'},
            'user': {'GET': '*', 'POST': 'restricted', 'PUT': 'own', 'DELETE': 'none'},
        }
        
        role_perms = permission_map.get(user_role, {})
        method_perm = role_perms.get(method, 'none')
        
        if method_perm == '*':
            return True, "Full access"
        elif method_perm == 'restricted':
            if 'admin' in endpoint or 'delete' in endpoint:
                return False, f"Role {user_role} cannot access {endpoint}"
            return True, "Limited access"
        elif method_perm == 'own':
            return True, "Access to own resources only"
        else:
            return False, f"Role {user_role} has no {method} permission"
    
    def calculate_risk_score(self, request_metadata: Dict[str, any]) -> float:
        """
        Calculate security risk score for request
        
        Args:
            request_metadata: Dict with metadata
            
        Returns:
            Risk score (0-1, higher = more risky)
        """
        risk_fields = [
            Field('ip_reputation_score', 75, -3.0, 3.0),  # Negative importance = inverse
            Field('failed_attempts', 0, -4.0, 4.0),
            Field('suspicious_patterns', False, -4.0, 5.0),
            Field('known_attacker_signature', False, -5.0, 5.0)
        ]
        
        config = {field.name: field.to_dict() for field in risk_fields}
        risk_formula = AdaptiveFormula(config, tier=self.tier, license_key=self.license_key)
        
        # Invert score since we're measuring risk
        safety_score = risk_formula.evaluate(request_metadata)
        risk_score = 1.0 - safety_score
        
        return risk_score
    
    def adjust_sensitivity(self, mode: str = 'normal'):
        """
        Adjust validation sensitivity based on security mode
        
        Args:
            mode: 'relaxed', 'normal', 'strict', 'lockdown'
        """
        sensitivity_map = {
            'relaxed': 0.55,
            'normal': 0.65,
            'strict': 0.75,
            'lockdown': 0.85
        }
        
        threshold = sensitivity_map.get(mode, 0.65)
        self.formula.set_confidence_level(threshold)
        
        return threshold
    
    def set_adjustment_factor(self, factor: float):
        """
        Set weight adjustment factor (Enterprise only)
        
        Args:
            factor: Adjustment factor (0.0-1.0)
                    0.0 = 100% expert weights
                    0.5 = 50/50 mix
                    1.0 = 100% algorithm weights
        """
        if self.tier != 'enterprise':
            raise ValueError("Weight adjustment requires Enterprise license")
        
        self.formula.set_adjustment_factor(factor)
    
    def get_metrics(self) -> Union[RequestMetrics, Dict]:
        """
        Get validation metrics (Professional/Enterprise feature)
        
        Returns:
            RequestMetrics or error dict for Community tier
        """
        metrics = self.formula.get_metrics()
        
        if 'error' in metrics:
            return metrics  # Community tier error message
        
        return RequestMetrics(
            total_validations=metrics['evaluations'],
            avg_score=metrics.get('avg_score', 0),
            current_threshold=metrics.get('current_confidence_level', 0.65),
            min_score=metrics.get('min_score', 0),
            max_score=metrics.get('max_score', 1),
            tier=metrics.get('tier', 'community'),
            license_valid=metrics.get('license_valid', False),
            adaptive_weights=metrics.get('adaptive_weights', False),
            weight_changes=metrics.get('weight_changes', {})
        )
    
    def get_tier_info(self) -> Dict:
        """Get information about current tier and features"""
        base_features = ['Basic validation', 'Standard fields', 'Dict support']
        
        tier_features = {
            'community': base_features,
            'professional': base_features + [
                'Adaptive threshold',
                'Performance metrics', 
                'Batch validation',
                'DataFrame support'
            ],
            'enterprise': base_features + [
                'Adaptive threshold',
                'Enhanced metrics',
                'Batch validation', 
                'DataFrame support',
                'Weight optimization',
                'Adjustment factor control',
                'Priority support'
            ]
        }
        
        return {
            'tier': self.tier,
            'features': tier_features.get(self.tier, base_features),
            'license_valid': self.formula.license_validated if self.tier != 'community' else True
        }
    
    def _get_validation_message(self, score: float, threshold: float) -> str:
        """Generate appropriate validation message"""
        if score > threshold + 0.2:
            return "Request validated successfully"
        elif score > threshold:
            return "Request validated with minor concerns"
        elif score > threshold - 0.1:
            return "Request failed validation - borderline"
        else:
            return "Request failed validation - multiple issues"
    
    def _analyze_validation(self, request: Dict, score: float) -> Dict:
        """Analyze which fields contributed most to validation result"""
        critical_fields = ['auth_token_present', 'user_verified', 'token_age_minutes']
        
        issues = []
        for field_name in critical_fields:
            if field_name in request:
                field_value = request[field_name]
                field_config = next((f for f in self.fields if f.name == field_name), None)
                
                if field_config and field_value != field_config.reference:
                    issues.append(f"{field_name}: expected {field_config.reference}, got {field_value}")
        
        details = {
            'score': score,
            'issues': issues,
            'field_count': len(self.fields),
            'tier': self.tier
        }
        
        # Add enterprise metrics if available
        if self.tier == 'enterprise' and hasattr(self.formula, 'weight_history'):
            if len(self.formula.weight_history) > 0:
                details['weights_optimized'] = True
                details['adjustment_factor'] = self.formula.adjustment_factor
        
        return details
    
    def add_custom_field(self, field: Field):
        """Add a custom field to validator"""
        self.fields.append(field)
        self._setup_formula(self.formula.get_confidence_level())
    
    def remove_field(self, field_name: str):
        """Remove a field from validator"""
        self.fields = [f for f in self.fields if f.name != field_name]
        self._setup_formula(self.formula.get_confidence_level())