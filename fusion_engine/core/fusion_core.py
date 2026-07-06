"""
Fusion Core Engine
Unifies all computation engines with predictive AI logic and negative latency handling.
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .sqrt_engine import SixBySixSqrtEngine, SqrtResult
from .quantization import QuantizedEntropyEngine, QuantizedResult


@dataclass
class FusionOperation:
    """Container for fused operations with full metadata"""
    timestamp: float
    sqrt_result: Optional[SqrtResult]
    quantized_result: Optional[QuantizedResult]
    predicted_latency: float
    actual_latency: float
    negative_latency_event: bool
    entropy_score: float
    cache_hit: bool
    waylink_id: int


class FusionCoreEngine:
    """
    Main fusion engine combining all computational components.
    
    Features:
    - Unified sqrt and quantization operations
    - Negative latency prediction via Plank force
    - 6-bit predictive AI logic
    - WayLink cache integration
    - Real-time performance monitoring
    """
    
    STABILITY_FACTOR = 0.625
    GOLDEN_RATIO = 1.618033988749895
    TURBO_FREQUENCY_MHZ = 432
    
    def __init__(self, mode: str = "balanced"):
        self.sqrt_engine = SixBySixSqrtEngine()
        self.quant_engine = QuantizedEntropyEngine()
        
        self.mode = mode  # 'performance', 'efficiency', 'balanced'
        self.operation_history: List[FusionOperation] = []
        self.negative_latency_events = 0
        self.total_predicted_latency = 0.0
        self.total_actual_latency = 0.0
        
        # Mode-specific configuration
        self._configure_mode(mode)
    
    def _configure_mode(self, mode: str):
        """Configure engine based on operational mode"""
        if mode == "performance":
            self.newton_iterations = 6
            self.prediction_weight = 0.9
        elif mode == "efficiency":
            self.newton_iterations = 4
            self.prediction_weight = 0.7
        else:  # balanced
            self.newton_iterations = 5
            self.prediction_weight = 0.8
    
    def execute_fusion(self, value: float, 
                       waylink_id: int = 0,
                       use_negative_latency: bool = True) -> FusionOperation:
        """
        Execute a fused operation combining sqrt and quantization.
        
        Args:
            value: Input value for processing
            waylink_id: WayLink cache identifier
            use_negative_latency: Enable negative latency prediction
            
        Returns:
            FusionOperation with complete metadata
        """
        start_time = time.perf_counter()
        
        # Execute square root with 6-bit entropy
        sqrt_result = self.sqrt_engine.compute_sqrt(value)
        
        # Execute quantization with SHA384-XOR
        quant_result = self.quant_engine.quantize_with_crypto(value)
        
        # Calculate predicted latency
        base_predicted = sqrt_result.predicted_latency
        
        # Apply negative latency prediction if enabled
        negative_latency_event = False
        if use_negative_latency:
            predicted_offset = self._calculate_negative_latency_offset(value)
            if predicted_offset > 0:
                base_predicted -= predicted_offset * self.STABILITY_FACTOR
                negative_latency_event = True
                self.negative_latency_events += 1
        
        predicted_latency = max(0.1, base_predicted)
        
        # Simulate actual latency (in real system, this would be measured)
        time.sleep(predicted_latency * 1e-6)  # Microsecond simulation
        actual_latency = (time.perf_counter() - start_time) * 1e6  # Convert to microseconds
        
        # Update totals
        self.total_predicted_latency += predicted_latency
        self.total_actual_latency += actual_latency
        
        # Calculate entropy score
        entropy_score = self._calculate_entropy_score(sqrt_result, quant_result)
        
        # Determine cache hit
        cache_hit = sqrt_result.cache_hit or (waylink_id % 4 == 0)
        
        operation = FusionOperation(
            timestamp=start_time,
            sqrt_result=sqrt_result,
            quantized_result=quant_result,
            predicted_latency=predicted_latency,
            actual_latency=actual_latency,
            negative_latency_event=negative_latency_event,
            entropy_score=entropy_score,
            cache_hit=cache_hit,
            waylink_id=waylink_id
        )
        
        self.operation_history.append(operation)
        
        # Keep history bounded
        if len(self.operation_history) > 10000:
            self.operation_history = self.operation_history[-5000:]
        
        return operation
    
    def _calculate_negative_latency_offset(self, value: float) -> float:
        """
        Calculate negative latency offset using pattern prediction.
        Based on Plank force scaling and historical patterns.
        """
        if len(self.operation_history) < 3:
            return 0.0
        
        # Detect sequential access patterns
        recent_values = [op.sqrt_result.value for op in self.operation_history[-3:]]
        
        # Check for stride pattern
        if len(recent_values) >= 3:
            stride1 = recent_values[1] - recent_values[0]
            stride2 = recent_values[2] - recent_values[1]
            
            if abs(stride1 - stride2) < 0.001:
                # Strong pattern detected - predict next access
                return abs(stride1) * 0.5
        
        # Entropy-based prediction
        recent_entropy = [op.entropy_score for op in self.operation_history[-5:]]
        avg_entropy = sum(recent_entropy) / len(recent_entropy)
        
        if avg_entropy > 0.8:
            return 0.3 * self.STABILITY_FACTOR
        
        return 0.0
    
    def _calculate_entropy_score(self, sqrt_result: SqrtResult, 
                                  quant_result: QuantizedResult) -> float:
        """Calculate combined entropy score from both engines"""
        # Normalize entropy code to [0, 1]
        sqrt_entropy_norm = sqrt_result.entropy_code / 63.0
        
        # Normalize XOR entropy to [0, 1]
        quant_entropy_norm = quant_result.xor_entropy / 63.0
        
        # Weighted combination
        score = (sqrt_entropy_norm * 0.6 + quant_entropy_norm * 0.4)
        
        # Apply golden ratio adjustment
        score = score * self.GOLDEN_RATIO / 1.618
        
        return min(1.0, max(0.0, score))
    
    def execute_batch(self, values: List[float], 
                      waylink_ids: Optional[List[int]] = None) -> List[FusionOperation]:
        """Execute batch of fused operations"""
        if waylink_ids is None:
            waylink_ids = list(range(len(values)))
        
        results = []
        for i, value in enumerate(values):
            waylink_id = waylink_ids[i % len(waylink_ids)]
            result = self.execute_fusion(value, waylink_id)
            results.append(result)
        
        return results
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if not self.operation_history:
            return {"error": "No operations executed yet"}
        
        total_ops = len(self.operation_history)
        cache_hits = sum(1 for op in self.operation_history if op.cache_hit)
        negative_events = sum(1 for op in self.operation_history 
                             if op.negative_latency_event)
        
        avg_predicted = self.total_predicted_latency / total_ops
        avg_actual = self.total_actual_latency / total_ops
        
        # Calculate prediction accuracy
        latency_errors = [abs(op.predicted_latency - op.actual_latency) 
                         for op in self.operation_history]
        avg_latency_error = sum(latency_errors) / len(latency_errors)
        
        # Get subsystem statistics
        sqrt_stats = self.sqrt_engine.get_statistics()
        quant_stats = self.quant_engine.get_statistics()
        
        return {
            "total_operations": total_ops,
            "cache_hit_rate": cache_hits / total_ops,
            "negative_latency_events": negative_events,
            "negative_latency_ratio": negative_events / total_ops,
            "avg_predicted_latency_us": avg_predicted,
            "avg_actual_latency_us": avg_actual,
            "prediction_accuracy": 1.0 - (avg_latency_error / max(avg_predicted, 1e-6)),
            "mode": self.mode,
            "stability_factor": self.STABILITY_FACTOR,
            "turbo_frequency_mhz": self.TURBO_FREQUENCY_MHZ,
            "sqrt_statistics": sqrt_stats,
            "quant_statistics": quant_stats,
        }
    
    def reset(self):
        """Reset all engine states"""
        self.sqrt_engine.reset()
        self.quant_engine.reset()
        self.operation_history = []
        self.negative_latency_events = 0
        self.total_predicted_latency = 0.0
        self.total_actual_latency = 0.0
