# Pure Python fallback when Cython is not available
from typing import Dict, List, Any, Tuple, Optional
from math import sqrt

class Field:
    """Field configuration for adaptive formula"""
    def __init__(self, name: str, reference: Any, importance: float = 1.0, sensitivity: float = 1.5):
        self.name = name
        self.reference = reference
        self.importance = importance
        self.sensitivity = sensitivity
    
    def to_dict(self):
        return {
            'default': self.reference,
            'weight': self.importance,
            'criticality': self.sensitivity
        }

class AdaptiveFormula:
    """Pure Python implementation of core formula"""
    
    def __init__(self, config: Dict, tier: str = 'community', license_key: str = None):
        self.config = config
        self.tier = tier
        self.license_key = license_key
        self.threshold = 0.65
        self.penalty_base = 0.02
        self.history = []
        self.license_validated = False
        self.weight_history = {}
        self.magnitude_cache = {}
        self.adjustment_factor = 0.3  # 70% expert, 30% algorithm
        
        # Validate license for premium tiers
        if tier != 'community':
            self.license_validated = self._validate_license()
            if not self.license_validated:
                print(f"Warning: Invalid license for {tier} tier. Falling back to community.")
                self.tier = 'community'
        
        self.ml_model = None if self.tier == 'community' else self._init_ml()
    
    def _validate_license(self):
        """Validate license key with expiration date"""
        if not self.license_key:
            return False
        
        from datetime import datetime
        
        # Format: PRO-YYYY-MM-DD-XXXX-XXXX or ENT-YYYY-MM-DD-XXXX-XXXX
        try:
            parts = self.license_key.split('-')
            if len(parts) < 6:
                return False
            
            tier_prefix = parts[0]
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            
            # Check tier match
            if self.tier == 'professional' and tier_prefix != 'PRO':
                return False
            elif self.tier == 'enterprise' and tier_prefix != 'ENT':
                return False
            
            # Check expiration
            expiry_date = datetime(year, month, day)
            today = datetime.now()
            
            if today > expiry_date:
                print(f"License expired on {expiry_date.date()}. Renew at licensing@adaptiveformula.ai")
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def calculate_similarity(self, value, reference):
        """Protected similarity calculation"""
        if value is None:
            return 0.0
            
        if isinstance(value, (int, float)) and isinstance(reference, (int, float)):
            # Numerical similarity
            if abs(float(value)) + abs(float(reference)) < 1e-5:
                return 1.0
            sim = 1.0 - abs(float(value) - float(reference)) / (abs(float(value)) + abs(float(reference)) + 1e-5)
            return max(0.0, min(1.0, sim))
        elif isinstance(value, str) and isinstance(reference, str):
            # String similarity
            return 1.0 if value == reference else 0.3
        elif isinstance(value, bool) and isinstance(reference, bool):
            # Boolean similarity
            return 1.0 if value == reference else 0.0
        else:
            # Default similarity for unknown types
            return 0.5
    
    def evaluate(self, data: dict) -> float:
        """Main scoring function with adaptive learning"""
        numerator = 0.0
        denominator = 0.0
        
        for field_name, field_config in self.config.items():
            value = data.get(field_name)
            reference = field_config.get('default')
            weight = float(field_config.get('weight', 1.0))
            criticality = float(field_config.get('criticality', 1.5))
            
            similarity = self.calculate_similarity(value, reference)
            
            # Apply ML optimization if available (Pro/Enterprise)
            if self.tier != 'community' and self.ml_model is not None:
                weight, criticality = self._optimize_params(field_name, similarity, value)
            
            numerator += similarity * weight * criticality
            denominator += weight * criticality
        
        score = numerator / denominator if denominator > 0 else 0.0
        
        # Apply penalty
        score *= (1.0 - self.penalty_base)
        
        # Adaptive learning for premium tiers
        if self.tier != 'community':
            self._update_history(score)
        
        return score
    
    def _update_history(self, score: float):
        """Update history and adapt threshold - Premium feature"""
        self.history.append(score)
        
        # Keep only last 100 evaluations
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # Adaptive threshold adjustment after minimum history
        if len(self.history) > 10:
            recent_scores = self.history[-10:]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            # Gradual threshold adjustment
            self.threshold = 0.65 + (avg_score - 0.5) * 0.1
            self.threshold = max(0.4, min(0.9, self.threshold))  # Keep in reasonable range
    
    def _optimize_params(self, field_name: str, similarity: float, value) -> tuple:
        """ML optimization - Enterprise/Pro with weight calibration"""
        # Get expert weights from config
        expert_weight = float(self.config[field_name].get('weight', 1.0))
        expert_criticality = float(self.config[field_name].get('criticality', 1.5))
        
        if self.tier == 'enterprise' and len(self.history) > 20:
            # ENTERPRISE: Formula 1 - Calibración de Pesos
            
            # Update magnitude cache for this field
            if field_name not in self.magnitude_cache:
                self.magnitude_cache[field_name] = []
            
            # Store recent values for magnitude calculation
            if isinstance(value, (int, float)):
                self.magnitude_cache[field_name].append(abs(float(value)))
                if len(self.magnitude_cache[field_name]) > 50:
                    self.magnitude_cache[field_name] = self.magnitude_cache[field_name][-50:]
            
            # Calculate proposed weight based on magnitude
            if field_name in self.magnitude_cache and len(self.magnitude_cache[field_name]) > 5:
                # Suma de magnitudes con amortiguación (sqrt)
                magnitude = sum(self.magnitude_cache[field_name])
                normalized_magnitude = sqrt(magnitude) if magnitude > 0 else 1.0
                
                # Normalize across all fields (simplified for this field)
                proposed_weight = normalized_magnitude / (normalized_magnitude + 1.0)
                
                # Mix expert and proposed weights
                final_weight = (1 - self.adjustment_factor) * expert_weight + self.adjustment_factor * proposed_weight
                
                # Track weight evolution
                if field_name not in self.weight_history:
                    self.weight_history[field_name] = []
                self.weight_history[field_name].append(final_weight)
                
                # Apply performance-based criticality adjustment
                history_avg = sum(self.history[-20:]) / 20.0
                optimized_criticality = expert_criticality * (1.0 + (1.0 - similarity) * history_avg)
                
                return (final_weight, optimized_criticality)
            else:
                # Not enough data, use enhanced basic optimization
                history_avg = sum(self.history[-20:]) / 20.0
                optimized_weight = expert_weight * (1.0 + similarity * history_avg * 0.2)
                optimized_criticality = expert_criticality * (1.0 + (1.0 - similarity) * history_avg * 0.3)
                return (optimized_weight, optimized_criticality)
            
        elif self.tier == 'professional':
            # PROFESSIONAL: Basic optimization (existing)
            optimized_weight = expert_weight * (1.0 + similarity * 0.1)
            optimized_criticality = expert_criticality * (1.0 + (1.0 - similarity) * 0.1)
            return (optimized_weight, optimized_criticality)
        else:
            # Community: no optimization
            return (expert_weight, expert_criticality)
    
    def _init_ml(self):
        """Initialize ML model for pro/enterprise tiers"""
        # Phase 1: Return placeholder with tier-specific config
        ml_config = {
            'initialized': True, 
            'tier': self.tier,
            'adaptive_weights': self.tier == 'enterprise',
            'adjustment_factor': self.adjustment_factor
        }
        return ml_config
    
    def process_heterogeneous(self, data):
        """Handle heterogeneous data - Pro/Enterprise only"""
        if self.tier == 'community':
            if not isinstance(data, dict):
                raise ValueError("Community tier only supports dict data")
            return data
        
        # Complex heterogeneous handling
        return self._normalize_complex_data(data)
    
    def _normalize_complex_data(self, data):
        """Protected normalization logic with Series support"""
        if isinstance(data, dict):
            return data
        
        # Handle pandas DataFrame AND Series
        if hasattr(data, '__class__'):
            class_name = data.__class__.__name__
            
            # Handle DataFrame
            if class_name == 'DataFrame':
                try:
                    import pandas as pd
                    if isinstance(data, pd.DataFrame):
                        return data.to_dict('records')[0] if len(data) > 0 else {}
                except ImportError:
                    raise ImportError(
                        "DataFrame support requires pandas. Install it with: pip install pandas\n"
                        "Professional and Enterprise tiers support DataFrames, but pandas must be installed separately."
                    )
            
            # Handle Series (what df.iloc[i] returns)
            elif class_name == 'Series':
                try:
                    import pandas as pd
                    if isinstance(data, pd.Series):
                        return data.to_dict()
                except ImportError:
                    raise ImportError(
                        "Series support requires pandas. Install it with: pip install pandas\n"
                        "Professional and Enterprise tiers support pandas data structures."
                    )
        
        # Handle numpy arrays
        try:
            import numpy as np
            if isinstance(data, np.ndarray):
                return {'array_data': data.tolist()}
        except ImportError:
            pass
        
        # Handle nested structures
        if hasattr(data, '__dict__'):
            return vars(data)
        
        return {'data': data}
    
    def get_confidence_level(self) -> float:
        """Get current confidence level"""
        return self.threshold
    
    def set_confidence_level(self, level: float):
        """Set confidence level manually"""
        self.threshold = max(0.0, min(1.0, level))
    
    def get_metrics(self) -> dict:
        """Get performance metrics - Premium feature"""
        if self.tier == 'community':
            return {'error': 'Metrics only available in Professional/Enterprise tiers'}
        
        if len(self.history) == 0:
            return {'evaluations': 0, 'avg_score': 0.0, 'current_threshold': self.threshold}
        
        metrics = {
            'evaluations': len(self.history),
            'avg_score': sum(self.history) / len(self.history),
            'min_score': min(self.history),
            'max_score': max(self.history),
            'current_confidence_level': self.threshold,
            'tier': self.tier,
            'license_valid': self.license_validated
        }
        
        # Enterprise: add weight evolution metrics
        if self.tier == 'enterprise' and len(self.weight_history) > 0:
            metrics['adaptive_weights'] = True
            metrics['adjusted_fields'] = list(self.weight_history.keys())
            metrics['adjustment_factor'] = self.adjustment_factor
            
            # Average weight change
            weight_changes = {}
            for field, history in self.weight_history.items():
                if len(history) > 1:
                    initial = self.config[field].get('weight', 1.0)
                    current = history[-1]
                    weight_changes[field] = (current - initial) / initial if initial > 0 else 0
            metrics['weight_changes'] = weight_changes
        
        return metrics
    
    def set_adjustment_factor(self, factor: float):
        """Set adjustment factor for Enterprise weight calibration"""
        if self.tier == 'enterprise':
            self.adjustment_factor = max(0.0, min(1.0, factor))