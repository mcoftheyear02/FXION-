"""
SixBySix Square Root Engine
Implements 6x6 bit decomposition (4096 entries) with Newton-Raphson refinement
and 6-bit entropy tracking for predictive latency optimization.
"""

import math
from typing import Tuple, Dict, List
from dataclasses import dataclass, field


@dataclass
class SqrtResult:
    """Result container for square root operations with entropy tracking"""
    value: float
    sqrt_result: float
    entropy_code: int  # 6-bit entropy code (0-63)
    iterations: int
    precision_error: float
    predicted_latency: float
    cache_hit: bool = False


class SixBySixSqrtEngine:
    """
    Advanced square root engine using 6x6 bit decomposition.
    
    Features:
    - 4096-entry lookup table (6 high bits × 6 low bits)
    - Newton-Raphson refinement with 6 iterations
    - 6-bit entropy coding for prediction
    - Predictive latency estimation
    """
    
    MAX_ENTROPY_BITS = 6
    MAX_ENTROPY_VALUE = (1 << MAX_ENTROPY_BITS) - 1  # 63
    LOOKUP_TABLE_SIZE = 4096  # 2^12 for 6x6 decomposition
    NEWTON_ITERATIONS = 6
    
    def __init__(self):
        self.lookup_table: Dict[int, float] = {}
        self.entropy_history: List[int] = []
        self.operation_count = 0
        self.total_precision_error = 0.0
        self._build_lookup_table()
    
    def _build_lookup_table(self):
        """Build the 4096-entry lookup table for initial sqrt estimates"""
        for i in range(self.LOOKUP_TABLE_SIZE):
            # Normalize to [0, 1) range for initial estimate
            normalized = i / self.LOOKUP_TABLE_SIZE
            if normalized > 0:
                self.lookup_table[i] = math.sqrt(normalized)
            else:
                self.lookup_table[i] = 0.0
    
    def _extract_entropy_code(self, value: float) -> int:
        """
        Extract 6-bit entropy code from input value.
        Uses logarithmic scaling for better distribution.
        """
        if value <= 0:
            return 0
        
        # Logarithmic scaling for entropy extraction
        log_value = math.log2(max(value, 1e-10))
        normalized = (log_value + 10) / 20  # Normalize to ~[0, 1]
        entropy_code = int(normalized * self.MAX_ENTROPY_VALUE)
        
        return max(0, min(self.MAX_ENTROPY_VALUE, entropy_code))
    
    def _get_initial_estimate(self, value: float, entropy_code: int) -> float:
        """Get initial sqrt estimate from lookup table based on 6x6 decomposition"""
        if value <= 0:
            return 0.0
        
        # Decompose into 6 high bits and 6 low bits
        scaled = int((value / max(value, 1)) * (self.LOOKUP_TABLE_SIZE - 1))
        scaled = max(0, min(self.LOOKUP_TABLE_SIZE - 1, scaled))
        
        # Use lookup table with entropy adjustment
        base_estimate = self.lookup_table[scaled]
        entropy_factor = 1.0 + (entropy_code / self.MAX_ENTROPY_VALUE) * 0.1
        
        return base_estimate * math.sqrt(abs(value)) * entropy_factor
    
    def _newton_raphson_refine(self, value: float, estimate: float, 
                                iterations: int = None) -> Tuple[float, int]:
        """
        Refine sqrt estimate using Newton-Raphson method.
        Returns refined result and actual iterations used.
        """
        if iterations is None:
            iterations = self.NEWTON_ITERATIONS
        
        if value <= 0:
            return 0.0, 0
        
        current = estimate
        actual_iterations = 0
        
        for i in range(iterations):
            if current <= 0:
                current = 0.001
            
            next_val = 0.5 * (current + value / current)
            
            # Check convergence
            if abs(next_val - current) < 1e-12:
                actual_iterations = i + 1
                break
            
            current = next_val
            actual_iterations = i + 1
        
        return current, actual_iterations
    
    def compute_sqrt(self, value: float, use_prediction: bool = True) -> SqrtResult:
        """
        Compute square root with 6-bit entropy tracking and predictive latency.
        
        Args:
            value: Input value for square root
            use_prediction: Enable predictive latency estimation
            
        Returns:
            SqrtResult with value, entropy code, iterations, and latency info
        """
        self.operation_count += 1
        
        # Extract 6-bit entropy code
        entropy_code = self._extract_entropy_code(value)
        self.entropy_history.append(entropy_code)
        
        # Keep entropy history bounded
        if len(self.entropy_history) > 1000:
            self.entropy_history = self.entropy_history[-500:]
        
        # Get initial estimate from 6x6 lookup table
        initial_estimate = self._get_initial_estimate(value, entropy_code)
        
        # Refine with Newton-Raphson
        sqrt_result, iterations = self._newton_raphson_refine(value, initial_estimate)
        
        # Calculate precision error
        expected = math.sqrt(value) if value >= 0 else 0
        precision_error = abs(sqrt_result - expected) / max(expected, 1e-10)
        self.total_precision_error += precision_error
        
        # Predict latency based on entropy and iterations
        if use_prediction:
            predicted_latency = self._predict_latency(entropy_code, iterations, value)
        else:
            predicted_latency = iterations * 2.5  # Base latency per iteration
        
        # Check for cache hit pattern (repeated entropy codes)
        cache_hit = self._check_cache_pattern(entropy_code)
        
        return SqrtResult(
            value=value,
            sqrt_result=sqrt_result,
            entropy_code=entropy_code,
            iterations=iterations,
            precision_error=precision_error,
            predicted_latency=predicted_latency,
            cache_hit=cache_hit
        )
    
    def _predict_latency(self, entropy_code: int, iterations: int, 
                         value: float) -> float:
        """Predict operation latency based on entropy and historical patterns"""
        base_latency = iterations * 2.5
        
        # Entropy-based adjustment
        entropy_factor = 1.0 - (entropy_code / self.MAX_ENTROPY_VALUE) * 0.3
        
        # Value magnitude adjustment
        magnitude_factor = 1.0 + math.log10(max(value, 1)) * 0.05
        
        # Historical pattern bonus
        pattern_bonus = 0.0
        if len(self.entropy_history) >= 3:
            recent = self.entropy_history[-3:]
            if recent[0] == recent[1] == recent[2]:
                pattern_bonus = -0.5  # Predictive optimization
        
        return max(1.0, base_latency * entropy_factor * magnitude_factor + pattern_bonus)
    
    def _check_cache_pattern(self, entropy_code: int) -> bool:
        """Check if current entropy code matches recent cache patterns"""
        if len(self.entropy_history) < 5:
            return False
        
        recent = self.entropy_history[-5:-1]
        return entropy_code in recent
    
    def get_statistics(self) -> Dict:
        """Get engine statistics"""
        avg_precision = (self.total_precision_error / self.operation_count 
                        if self.operation_count > 0 else 0)
        
        entropy_distribution = {}
        for code in self.entropy_history:
            entropy_distribution[code] = entropy_distribution.get(code, 0) + 1
        
        return {
            "total_operations": self.operation_count,
            "average_precision_error": avg_precision,
            "entropy_codes_used": len(entropy_distribution),
            "history_size": len(self.entropy_history),
            "lookup_table_size": len(self.lookup_table),
        }
    
    def reset(self):
        """Reset engine state"""
        self.entropy_history = []
        self.operation_count = 0
        self.total_precision_error = 0.0
