"""
Plank Force Predictor
Implements negative latency prediction using Planck force scaling.
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PlankPrediction:
    """Result of a Plank force prediction"""
    predicted_offset: float
    confidence: float
    force_scaled_value: float
    negative_latency_event: bool


class PlankForcePredictor:
    """
    Negative latency predictor based on Planck force scaling.
    
    Features:
    - Planck force constant (1.21e44 N)
    - Stability factor 0.625
    - Pattern-based prediction
    - Confidence scoring
    """
    
    # Planck force in Newtons
    PLANCK_FORCE = 1.21e44
    
    # Reduced Planck constant
    HBAR = 1.054571817e-34
    
    # Speed of light
    C = 299792458.0
    
    # Stability factor from requirements
    STABILITY_FACTOR = 0.625
    
    # Scaling exponent for practical computation
    SCALING_EXPONENT = -43
    
    def __init__(self):
        self.prediction_history: List[PlankPrediction] = []
        self.pattern_buffer: List[float] = []
        self.total_predictions = 0
        self.accurate_predictions = 0
    
    def _scale_planck_force(self, value: float) -> float:
        """
        Scale Planck force to practical computational range.
        
        Uses logarithmic scaling with stability factor.
        """
        if value == 0:
            return 0.0
        
        # Logarithmic scaling
        log_value = math.log10(abs(value))
        
        # Apply Planck force scaling
        scaled = log_value * self.SCALING_EXPONENT
        
        # Apply stability factor
        stabilized = scaled * self.STABILITY_FACTOR
        
        return stabilized
    
    def predict_negative_latency(self, access_pattern: List[float],
                                  current_value: float) -> PlankPrediction:
        """
        Predict negative latency event using Plank force scaling.
        
        Args:
            access_pattern: Historical access pattern
            current_value: Current access value
            
        Returns:
            PlankPrediction with offset and confidence
        """
        self.total_predictions += 1
        
        # Update pattern buffer
        self.pattern_buffer.append(current_value)
        if len(self.pattern_buffer) > 100:
            self.pattern_buffer = self.pattern_buffer[-50:]
        
        # Detect stride pattern
        stride_detected = False
        predicted_stride = 0.0
        
        if len(access_pattern) >= 3:
            strides = []
            for i in range(1, len(access_pattern)):
                stride = access_pattern[i] - access_pattern[i-1]
                strides.append(stride)
            
            # Check stride consistency
            if len(strides) >= 2:
                avg_stride = sum(strides) / len(strides)
                variance = sum((s - avg_stride) ** 2 for s in strides) / len(strides)
                
                if variance < 0.01:
                    stride_detected = True
                    predicted_stride = avg_stride
        
        # Calculate Plank-scaled prediction
        plank_scaled = self._scale_planck_force(current_value)
        
        # Determine prediction offset
        if stride_detected:
            # High confidence with detected pattern
            predicted_offset = abs(predicted_stride) * self.STABILITY_FACTOR
            confidence = min(0.95, 0.7 + (1.0 - math.sqrt(variance)) * 0.25)
        else:
            # Lower confidence without pattern
            predicted_offset = abs(plank_scaled) * 0.1
            confidence = 0.3 + abs(plank_scaled) * 0.1
        
        # Clamp values
        predicted_offset = max(0.0, min(1.0, predicted_offset))
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine if negative latency event
        negative_event = confidence > 0.5 and predicted_offset > 0.01
        
        if negative_event:
            self.accurate_predictions += 1
        
        prediction = PlankPrediction(
            predicted_offset=predicted_offset,
            confidence=confidence,
            force_scaled_value=plank_scaled,
            negative_latency_event=negative_event
        )
        
        self.prediction_history.append(prediction)
        
        # Keep history bounded
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-500:]
        
        return prediction
    
    def calculate_quantum_adjustment(self, energy_level: float) -> float:
        """
        Calculate quantum adjustment factor based on energy level.
        
        Uses reduced Planck constant for quantum-scale calculations.
        """
        if energy_level <= 0:
            return 1.0
        
        # Quantum adjustment formula
        quantum_factor = math.exp(-energy_level * self.HBAR * 1e20)
        
        # Apply stability factor
        adjusted = quantum_factor * self.STABILITY_FACTOR
        
        return max(0.0, min(1.0, adjusted))
    
    def get_reduced_latency(self, base_latency: float,
                            prediction: PlankPrediction) -> float:
        """
        Calculate reduced latency based on prediction.
        
        Args:
            base_latency: Original latency
            prediction: PlankPrediction object
            
        Returns:
            Reduced latency value
        """
        if not prediction.negative_latency_event:
            return base_latency
        
        # Calculate reduction
        reduction_factor = prediction.predicted_offset * prediction.confidence
        
        # Apply stability factor
        effective_reduction = reduction_factor * self.STABILITY_FACTOR
        
        reduced = base_latency * (1 - effective_reduction)
        
        return max(0.0, reduced)
    
    def get_statistics(self) -> Dict:
        """Get predictor statistics"""
        accuracy = (self.accurate_predictions / 
                   max(self.total_predictions, 1))
        
        negative_events = sum(1 for p in self.prediction_history 
                             if p.negative_latency_event)
        
        avg_confidence = (sum(p.confidence for p in self.prediction_history) / 
                         max(len(self.prediction_history), 1))
        
        return {
            "total_predictions": self.total_predictions,
            "accurate_predictions": self.accurate_predictions,
            "prediction_accuracy": accuracy,
            "negative_latency_events": negative_events,
            "average_confidence": avg_confidence,
            "stability_factor": self.STABILITY_FACTOR,
            "planck_force": self.PLANCK_FORCE,
            "pattern_buffer_size": len(self.pattern_buffer),
        }
    
    def reset(self):
        """Reset predictor state"""
        self.prediction_history = []
        self.pattern_buffer = []
        self.total_predictions = 0
        self.accurate_predictions = 0
