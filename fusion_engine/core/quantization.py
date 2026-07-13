"""
Quantized Entropy Engine
Implements 4096→6-bit quantization with SHA384-XOR mixing for cryptographic entropy.
"""

import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QuantizedResult:
    """Result container for quantization operations"""
    original_value: float
    quantized_value: int  # 6-bit value (0-63)
    sha384_hash: str
    xor_entropy: int
    signature: str


class QuantizedEntropyEngine:
    """
    Advanced quantization engine with cryptographic mixing.
    
    Features:
    - Non-linear quantization table (4096 levels → 64 values)
    - SHA384 cryptographic hashing
    - XOR-based entropy mixing
    - Signature generation for validation
    """
    
    INPUT_LEVELS = 4096
    OUTPUT_BITS = 6
    OUTPUT_LEVELS = (1 << OUTPUT_BITS)  # 64
    
    def __init__(self):
        self.quantization_table: List[int] = []
        self.reverse_table: Dict[int, List[int]] = {}
        self.operation_history: List[QuantizedResult] = []
        self.entropy_accumulator = 0
        self._build_quantization_table()
    
    def _build_quantization_table(self):
        """Build non-linear quantization table for better distribution"""
        self.quantization_table = []
        self.reverse_table = {i: [] for i in range(self.OUTPUT_LEVELS)}
        
        for i in range(self.INPUT_LEVELS):
            # Non-linear mapping using logarithmic scaling
            normalized = i / (self.INPUT_LEVELS - 1)
            
            # Apply gamma correction for perceptual uniformity
            gamma = 0.625  # Stability factor from requirements
            adjusted = pow(normalized, gamma)
            
            # Map to 6-bit output
            quantized = int(adjusted * (self.OUTPUT_LEVELS - 1))
            quantized = max(0, min(self.OUTPUT_LEVELS - 1, quantized))
            
            self.quantization_table.append(quantized)
            self.reverse_table[quantized].append(i)
    
    def quantize(self, value: float) -> int:
        """
        Quantize a floating-point value to 6-bit representation.
        
        Args:
            value: Input value (will be normalized to [0, 4095])
            
        Returns:
            6-bit quantized value (0-63)
        """
        # Normalize input to [0, 4095] range
        normalized = int(abs(value) * 1000) % self.INPUT_LEVELS
        
        return self.quantization_table[normalized]
    
    def compute_sha384(self, data: bytes) -> str:
        """Compute SHA384 hash of input data"""
        return hashlib.sha384(data).hexdigest()
    
    def xor_mix(self, value1: int, value2: int) -> int:
        """XOR two values and return 6-bit result"""
        return (value1 ^ value2) & 0x3F  # Mask to 6 bits
    
    def quantize_with_crypto(self, value: float, 
                             seed: int = 0) -> QuantizedResult:
        """
        Perform quantization with SHA384-XOR cryptographic mixing.
        
        Args:
            value: Input value to quantize
            seed: Optional seed for entropy variation
            
        Returns:
            QuantizedResult with hash, XOR entropy, and signature
        """
        # Basic quantization
        quantized = self.quantize(value)
        
        # Update entropy accumulator
        self.entropy_accumulator = self.xor_mix(self.entropy_accumulator, quantized)
        
        # Create data for hashing
        data_bytes = (str(value) + str(seed) + str(self.entropy_accumulator)).encode('utf-8')
        sha384_hash = self.compute_sha384(data_bytes)
        
        # Extract XOR entropy from hash (first 6 bits)
        hash_int = int(sha384_hash[:8], 16)
        xor_entropy = hash_int & 0x3F
        
        # Mix quantized value with XOR entropy
        mixed_value = self.xor_mix(quantized, xor_entropy)
        
        # Generate signature
        signature_data = f"{value}:{quantized}:{xor_entropy}:{mixed_value}"
        signature = self.compute_sha384(signature_data.encode())[:16]
        
        result = QuantizedResult(
            original_value=value,
            quantized_value=quantized,
            sha384_hash=sha384_hash,
            xor_entropy=xor_entropy,
            signature=signature
        )
        
        self.operation_history.append(result)
        
        # Keep history bounded
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-500:]
        
        return result
    
    def dequantize(self, quantized_value: int) -> List[float]:
        """
        Dequantize a 6-bit value back to possible original ranges.
        
        Args:
            quantized_value: 6-bit value (0-63)
            
        Returns:
            List of possible original values (normalized)
        """
        quantized_value = max(0, min(self.OUTPUT_LEVELS - 1, quantized_value))
        original_indices = self.reverse_table.get(quantized_value, [])
        
        return [idx / (self.INPUT_LEVELS - 1) for idx in original_indices]
    
    def get_quantization_distribution(self) -> Dict[int, int]:
        """Get distribution of quantized values in history"""
        distribution = {i: 0 for i in range(self.OUTPUT_LEVELS)}
        
        for result in self.operation_history:
            distribution[result.quantized_value] += 1
        
        return distribution
    
    def get_statistics(self) -> Dict:
        """Get engine statistics"""
        distribution = self.get_quantization_distribution()
        unique_values = sum(1 for count in distribution.values() if count > 0)
        
        return {
            "total_operations": len(self.operation_history),
            "unique_quantized_values": unique_values,
            "entropy_accumulator": self.entropy_accumulator,
            "quantization_table_size": len(self.quantization_table),
            "distribution": distribution,
        }
    
    def reset(self):
        """Reset engine state"""
        self.operation_history = []
        self.entropy_accumulator = 0
