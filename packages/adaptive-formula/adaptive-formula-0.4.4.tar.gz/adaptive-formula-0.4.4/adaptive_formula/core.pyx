# Pure Python fallback when Cython is not available
from typing import Dict, List, Any, Tuple, Optional

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
        self.adjustment_factor = 0.3
        
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
        
        try:
            parts = self.license_key.split('-')
            if len(parts) < 6:
                return False
            
            tier_prefix = parts[0]
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            
            if self.tier == 'professional' and tier_prefix != 'PRO':
                return False
            elif self.tier == 'enterprise' and tier_prefix != 'ENT':
                return False
            
            expiry_date = datetime(year, month, day)
            today = datetime.now()
            
            if today > expiry_date:
                print(f"License expired on {expiry_date.date()}. Renew at licensing@adaptiveformula.ai")
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def calculate_similarity(self, value, reference):
        """Calculate similarity between value and reference"""
        if value is None:
            return 0.0
            
        if isinstance(value, (int, float)) and isinstance(reference, (int, float)):
            if abs(value) + abs(reference) < 1e-5:
                return 1.0
            sim = 1.0 - abs(value - reference) / (abs(value) + abs(reference) + 1e-5)
            return max(0.0, min(1.0, sim))
        elif isinstance(value, str) and isinstance(reference, str):
            return 1.0 if value == reference else 0.3
        elif isinstance(value, bool) and isinstance(reference, bool):
            return 1.0 if value == reference else 0.0
        else:
            return 0.5
    
    def evaluate(self, data: dict) -> float:
        """Main scoring function with adaptive learning"""
        numerator = 0.0
        denominator = 0.0
        
        for field_name, field_config in self.config.items():
            value = data.get(field_name)
            reference = field_config.get('default')
            weight = field_config.get('weight', 1.0)
            criticality = field_config.get('criticality', 1.5)
            
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
        """Update history and adapt threshold"""
        self.history.append(score)
        
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        if len(self.history) > 10:
            recent_scores = self.history[-10:]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            self.threshold = 0.65 + (avg_score - 0.5) * 0.1
            self.threshold = max(0.4, min(0.9, self.threshold))
    
    def _optimize_params(self, field_name: str, similarity: float, value):
        """ML optimization - simplified for pure Python"""
        expert_weight = self.config[field_name].get('weight', 1.0)
        expert_criticality = self.config[field_name].get('criticality', 1.5)
        
        if self.tier == 'enterprise' and len(self.history) > 20:
            # Simplified enterprise optimization
            history_avg = sum(self.history[-20:]) / 20.0
            optimized_weight = expert_weight * (1.0 + similarity * history_avg * 0.2)
            optimized_criticality = expert_criticality * (1.0 + (1.0 - similarity) * history_avg * 0.3)
            return (optimized_weight, optimized_criticality)
        elif self.tier == 'professional':
            optimized_weight = expert_weight * (1.0 + similarity * 0.1)
            optimized_criticality = expert_criticality * (1.0 + (1.0 - similarity) * 0.1)
            return (optimized_weight, optimized_criticality)
        else:
            return (expert_weight, expert_criticality)
    
    def _init_ml(self):
        """Initialize ML model placeholder"""
        return {
            'initialized': True, 
            'tier': self.tier,
            'adaptive_weights': self.tier == 'enterprise',
            'adjustment_factor': self.adjustment_factor
        }
    
    def process_heterogeneous(self, data):
        """Handle heterogeneous data"""
        if self.tier == 'community':
            if not isinstance(data, dict):
                raise ValueError("Community tier only supports dict data")
            return data
        
        return self._normalize_complex_data(data)
    
    def _normalize_complex_data(self, data):
        """Normalize complex data structures"""
        if isinstance(data, dict):
            return data
        
        if hasattr(data, '__class__'):
            class_name = data.__class__.__name__
            
            if class_name == 'DataFrame':
                try:
                    import pandas as pd
                    if isinstance(data, pd.DataFrame):
                        return data.to_dict('records')[0] if len(data) > 0 else {}
                except ImportError:
                    raise ImportError("DataFrame support requires pandas")
            
            elif class_name == 'Series':
                try:
                    import pandas as pd
                    if isinstance(data, pd.Series):
                        return data.to_dict()
                except ImportError:
                    raise ImportError("Series support requires pandas")
        
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
        """Get performance metrics"""
        if self.tier == 'community':
            return {'error': 'Metrics only available in Professional/Enterprise tiers'}
        
        if len(self.history) == 0:
            return {'evaluations': 0, 'avg_score': 0.0, 'current_threshold': self.threshold}
        
        return {
            'evaluations': len(self.history),
            'avg_score': sum(self.history) / len(self.history),
            'min_score': min(self.history),
            'max_score': max(self.history),
            'current_confidence_level': self.threshold,
            'tier': self.tier,
            'license_valid': self.license_validated
        }
    
    def set_adjustment_factor(self, factor: float):
        """Set adjustment factor for Enterprise weight calibration"""
        if self.tier == 'enterprise':
            self.adjustment_factor = max(0.0, min(1.0, factor))

class CognitiveSDK:
    """Main SDK interface"""
    
    def __init__(self, tier: str = 'community', license_key: str = None):
        self.tier = tier
        self.license_key = license_key
        self.formula = None
        self.config = {}
    
    def configure(self, fields: List[Field]):
        """Configure fields for evaluation"""
        self.config = {field.name: field.to_dict() for field in fields}
        self.formula = AdaptiveFormula(self.config, self.tier, self.license_key)
    
    def evaluate(self, data: Dict) -> float:
        """Evaluate data against configured rules"""
        if not self.formula:
            raise RuntimeError("SDK not configured. Call configure() first.")
        
        if self.tier != 'community' and not isinstance(data, dict):
            data = self.formula.process_heterogeneous(data)
        
        return self.formula.evaluate(data)
    
    def set_confidence_level(self, level: float):
        """Set decision confidence level"""
        if self.formula:
            self.formula.set_confidence_level(level)
    
    def get_confidence_level(self) -> float:
        """Get current confidence level"""
        return self.formula.get_confidence_level() if self.formula else 0.65
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        if not self.formula:
            return {'error': 'SDK not configured'}
        return self.formula.get_metrics()
    
    def set_adjustment_factor(self, factor: float):
        """Set weight adjustment factor"""
        if self.formula and self.tier == 'enterprise':
            self.formula.set_adjustment_factor(factor)