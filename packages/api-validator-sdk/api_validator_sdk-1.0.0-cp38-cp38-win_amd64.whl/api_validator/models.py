"""
Data models for API Validator with commercial features
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of API request validation"""
    is_valid: bool
    score: float
    threshold: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        return {
            'valid': self.is_valid,
            'score': round(self.score, 3),
            'threshold': round(self.threshold, 3),
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def to_response(self, status_code: Optional[int] = None) -> Dict:
        """Format as API response"""
        if status_code is None:
            status_code = 200 if self.is_valid else 403
        
        return {
            'status': status_code,
            'success': self.is_valid,
            'validation': self.to_dict()
        }

@dataclass
class RequestMetrics:
    """Enhanced metrics for request validation with tier features"""
    total_validations: int
    avg_score: float
    current_threshold: float
    min_score: float
    max_score: float
    tier: str = 'community'
    license_valid: bool = False
    adaptive_weights: bool = False
    weight_changes: Dict[str, float] = None
    
    def __post_init__(self):
        if self.weight_changes is None:
            self.weight_changes = {}
    
    def to_dict(self) -> Dict:
        result = {
            'total': self.total_validations,
            'average_score': round(self.avg_score, 3),
            'threshold': round(self.current_threshold, 3),
            'score_range': {
                'min': round(self.min_score, 3),
                'max': round(self.max_score, 3)
            },
            'tier': self.tier,
            'license_valid': self.license_valid
        }
        
        # Add enterprise features
        if self.tier == 'enterprise' and self.adaptive_weights:
            result['adaptive_weights'] = True
            if self.weight_changes:
                result['weight_optimization'] = {
                    'fields_optimized': len(self.weight_changes),
                    'avg_weight_change': round(sum(self.weight_changes.values()) / len(self.weight_changes), 3) if self.weight_changes else 0
                }
        
        return result

@dataclass
class ValidationConfig:
    """Configuration for validator with tier settings"""
    mode: str = 'normal'  # relaxed, normal, strict, lockdown
    use_standard_fields: bool = True
    custom_threshold: float = 0.65
    enable_metrics: bool = True
    enable_adaptive: bool = True
    tier: str = 'community'
    license_key: Optional[str] = None
    
    def get_threshold(self) -> float:
        """Get threshold based on mode"""
        thresholds = {
            'relaxed': 0.55,
            'normal': 0.65,
            'strict': 0.75,
            'lockdown': 0.85
        }
        return thresholds.get(self.mode, self.custom_threshold)
    
    def is_premium(self) -> bool:
        """Check if using premium features"""
        return self.tier in ['professional', 'enterprise']
    
    def has_enterprise_features(self) -> bool:
        """Check if enterprise features are available"""
        return self.tier == 'enterprise'

@dataclass
class APIRequest:
    """Structured API request data"""
    # Authentication
    auth_token: Optional[str] = None
    auth_token_present: bool = False
    auth_token_valid_length: bool = False
    token_age_minutes: float = 0.0
    user_id: Optional[str] = None
    user_verified: bool = False
    
    # Rate limiting
    requests_per_minute: int = 0
    requests_per_hour: int = 0
    daily_requests: int = 0
    
    # Payload
    payload_size_kb: float = 0.0
    content_type: str = 'application/json'
    
    # Security
    ip_address: Optional[str] = None
    ip_reputation_score: float = 100.0
    failed_attempts: int = 0
    user_agent: str = ''
    
    # Permissions
    user_role: str = 'user'
    endpoint: str = '/'
    method: str = 'GET'
    
    # Premium features
    user_plan: str = 'free'
    api_version: str = '1.0'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for validation"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class RateLimiter:
    """Advanced rate limiter with tier-based limits"""
    
    def __init__(self, tier: str = 'community'):
        self.tier = tier
        self.minute_window: List[datetime] = []
        self.hour_window: List[datetime] = []
        
        # Tier-based limits
        self.limits = {
            'community': {'per_minute': 60, 'per_hour': 1000},
            'professional': {'per_minute': 200, 'per_hour': 10000},
            'enterprise': {'per_minute': 1000, 'per_hour': 100000}
        }
    
    def get_limits(self) -> Dict[str, int]:
        """Get rate limits for current tier"""
        return self.limits.get(self.tier, self.limits['community'])
    
    def check_request(self, timestamp: datetime = None) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        if timestamp is None:
            timestamp = datetime.now()
        
        limits = self.get_limits()
        max_per_minute = limits['per_minute']
        max_per_hour = limits['per_hour']
        
        # Clean old entries
        minute_cutoff = timestamp.timestamp() - 60
        hour_cutoff = timestamp.timestamp() - 3600
        
        self.minute_window = [t for t in self.minute_window if t.timestamp() > minute_cutoff]
        self.hour_window = [t for t in self.hour_window if t.timestamp() > hour_cutoff]
        
        # Add current request
        self.minute_window.append(timestamp)
        self.hour_window.append(timestamp)
        
        # Check limits
        minute_count = len(self.minute_window)
        hour_count = len(self.hour_window)
        
        return {
            'requests_per_minute': minute_count,
            'requests_per_hour': hour_count,
            'minute_limit': max_per_minute,
            'hour_limit': max_per_hour,
            'minute_remaining': max(0, max_per_minute - minute_count),
            'hour_remaining': max(0, max_per_hour - hour_count),
            'minute_limit_exceeded': minute_count > max_per_minute,
            'hour_limit_exceeded': hour_count > max_per_hour,
            'allowed': minute_count <= max_per_minute and hour_count <= max_per_hour,
            'tier': self.tier
        }

@dataclass
class LicenseInfo:
    """License information for premium tiers"""
    tier: str
    license_key: str
    expiry_date: datetime
    is_valid: bool
    features: List[str]
    
    @classmethod
    def from_license_key(cls, license_key: str) -> 'LicenseInfo':
        """Parse license key and create LicenseInfo"""
        try:
            parts = license_key.split('-')
            if len(parts) < 6:
                return cls(
                    tier='community',
                    license_key='',
                    expiry_date=datetime.now(),
                    is_valid=False,
                    features=[]
                )
            
            tier_prefix = parts[0]
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            
            tier_map = {
                'PRO': 'professional',
                'ENT': 'enterprise'
            }
            
            tier = tier_map.get(tier_prefix, 'community')
            expiry_date = datetime(year, month, day)
            is_valid = datetime.now() <= expiry_date
            
            features_map = {
                'professional': [
                    'Adaptive threshold',
                    'Performance metrics',
                    'Batch validation',
                    'DataFrame support',
                    'Email support'
                ],
                'enterprise': [
                    'All Professional features',
                    'Weight optimization',
                    'Adjustment factor control',
                    'Unlimited validations',
                    'Priority support',
                    'Custom integrations'
                ]
            }
            
            return cls(
                tier=tier,
                license_key=license_key,
                expiry_date=expiry_date,
                is_valid=is_valid,
                features=features_map.get(tier, [])
            )
        except:
            return cls(
                tier='community',
                license_key='',
                expiry_date=datetime.now(),
                is_valid=False,
                features=[]
            )