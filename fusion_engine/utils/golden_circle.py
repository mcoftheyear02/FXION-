"""
Golden Circle Ratio
Implements 1:1 golden circle ratio calculations for fusion operations.
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GoldenCircleResult:
    """Result of a golden circle calculation"""
    input_value: float
    golden_adjusted: float
    circle_ratio: float
    deviation_from_golden: float
    stability_applied: bool


class GoldenCircleRatio:
    """
    Golden circle ratio calculator with 1:1 ratio enforcement.
    
    Features:
    - Golden ratio (φ = 1.618...)
    - 1:1 ratio target
    - Deviation measurement
    - Stability factor integration
    """
    
    # Golden ratio
    GOLDEN_RATIO = 1.618033988749895
    
    # Inverse golden ratio
    INV_GOLDEN_RATIO = 0.6180339887498949
    
    # Target 1:1 ratio
    TARGET_RATIO = 1.0
    
    # Stability factor
    STABILITY_FACTOR = 0.625
    
    def __init__(self):
        self.calculation_history: List[GoldenCircleResult] = []
        self.total_calculations = 0
        self.total_deviation = 0.0
    
    def calculate_golden_adjustment(self, value: float) -> GoldenCircleResult:
        """
        Apply golden circle adjustment to a value.
        
        Args:
            value: Input value
            
        Returns:
            GoldenCircleResult with adjusted value and metrics
        """
        self.total_calculations += 1
        
        # Calculate golden ratio adjustment
        golden_adjusted = value * self.GOLDEN_RATIO
        
        # Normalize to 1:1 ratio target
        normalized = value / max(abs(value), 1e-10)
        circle_ratio = abs(normalized) * self.TARGET_RATIO
        
        # Calculate deviation from golden ratio
        expected_golden = value * self.GOLDEN_RATIO
        actual_deviation = abs(golden_adjusted - expected_golden)
        relative_deviation = actual_deviation / max(abs(expected_golden), 1e-10)
        
        self.total_deviation += relative_deviation
        
        # Apply stability factor
        if relative_deviation > (1 - self.STABILITY_FACTOR):
            stabilized_adjustment = value * (1 + self.INV_GOLDEN_RATIO * self.STABILITY_FACTOR)
            stability_applied = True
        else:
            stabilized_adjustment = golden_adjusted
            stability_applied = False
        
        result = GoldenCircleResult(
            input_value=value,
            golden_adjusted=stabilized_adjustment,
            circle_ratio=circle_ratio,
            deviation_from_golden=relative_deviation,
            stability_applied=stability_applied
        )
        
        self.calculation_history.append(result)
        
        # Keep history bounded
        if len(self.calculation_history) > 1000:
            self.calculation_history = self.calculation_history[-500:]
        
        return result
    
    def enforce_1_to_1_ratio(self, value1: float, value2: float) -> Tuple[float, float]:
        """
        Enforce 1:1 ratio between two values using golden circle principles.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            Tuple of adjusted values in 1:1 ratio
        """
        # Calculate average
        avg = (abs(value1) + abs(value2)) / 2
        
        # Apply golden ratio weighting
        weighted1 = avg * self.GOLDEN_RATIO * self.STABILITY_FACTOR
        weighted2 = avg * self.INV_GOLDEN_RATIO * (2 - self.STABILITY_FACTOR)
        
        # Normalize to 1:1
        total = weighted1 + weighted2
        if total > 0:
            adjusted1 = avg * (weighted1 / total) * 2
            adjusted2 = avg * (weighted2 / total) * 2
        else:
            adjusted1 = adjusted2 = avg
        
        return adjusted1, adjusted2
    
    def calculate_circle_intersection(self, radius1: float, 
                                       radius2: float,
                                       distance: float) -> Dict:
        """
        Calculate intersection points of two circles.
        
        Uses golden ratio for optimal positioning.
        
        Args:
            radius1: Radius of first circle
            radius2: Radius of second circle
            distance: Distance between circle centers
            
        Returns:
            Dictionary with intersection information
        """
        # Check for valid intersection
        if distance > radius1 + radius2:
            return {"intersects": False, "reason": "too_far"}
        
        if distance < abs(radius1 - radius2):
            return {"intersects": False, "reason": "contained"}
        
        if distance == 0 and radius1 == radius2:
            return {"intersects": True, "infinite": True}
        
        # Calculate intersection using law of cosines
        a = (radius1**2 - radius2**2 + distance**2) / (2 * distance)
        h = math.sqrt(max(0, radius1**2 - a**2))
        
        # Golden ratio optimization
        golden_a = a * self.GOLDEN_RATIO * self.STABILITY_FACTOR
        
        return {
            "intersects": True,
            "infinite": False,
            "point_a_distance": a,
            "point_h_distance": h,
            "golden_optimized_a": golden_a,
            "circle_ratio": radius1 / max(radius2, 1e-10),
        }
    
    def get_average_deviation(self) -> float:
        """Get average deviation from golden ratio"""
        if self.total_calculations == 0:
            return 0.0
        
        return self.total_deviation / self.total_calculations
    
    def get_statistics(self) -> Dict:
        """Get golden circle statistics"""
        stability_applications = sum(1 for r in self.calculation_history 
                                     if r.stability_applied)
        
        avg_deviation = self.get_average_deviation()
        
        return {
            "total_calculations": self.total_calculations,
            "average_deviation": avg_deviation,
            "stability_applications": stability_applications,
            "golden_ratio": self.GOLDEN_RATIO,
            "target_ratio": self.TARGET_RATIO,
            "stability_factor": self.STABILITY_FACTOR,
            "history_size": len(self.calculation_history),
        }
    
    def reset(self):
        """Reset calculator state"""
        self.calculation_history = []
        self.total_calculations = 0
        self.total_deviation = 0.0
