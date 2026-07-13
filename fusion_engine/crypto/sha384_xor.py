"""
SHA384 XOR Mixer
Cryptographic entropy mixing using SHA384 and XOR operations.
"""

import hashlib
from typing import Tuple, List


class SHA384XORMixer:
    """
    Cryptographic mixer combining SHA384 hashing with XOR operations.
    
    Features:
    - SHA384 hash generation
    - 6-bit XOR entropy extraction
    - Multi-stage mixing
    - Entropy accumulation
    """
    
    HASH_LENGTH = 384
    ENTROPY_BITS = 6
    ENTROPY_MASK = 0x3F  # 6 bits
    
    def __init__(self):
        self.entropy_accumulator = 0
        self.mix_count = 0
        self.history: List[bytes] = []
    
    def compute_sha384(self, data: bytes) -> str:
        """Compute SHA384 hash of input data"""
        return hashlib.sha384(data).hexdigest()
    
    def extract_entropy(self, hash_hex: str, bit_offset: int = 0) -> int:
        """
        Extract 6-bit entropy from hash.
        
        Args:
            hash_hex: SHA384 hash in hex format
            bit_offset: Starting bit offset
            
        Returns:
            6-bit entropy value (0-63)
        """
        # Convert hex to integer
        hash_int = int(hash_hex[:16], 16)  # Use first 64 bits
        
        # Shift and mask to get 6 bits
        entropy = (hash_int >> bit_offset) & self.ENTROPY_MASK
        
        return entropy
    
    def xor_mix(self, value1: int, value2: int) -> int:
        """XOR two values and return 6-bit result"""
        return (value1 ^ value2) & self.ENTROPY_MASK
    
    def multi_stage_mix(self, data: bytes, stages: int = 3) -> Tuple[int, str]:
        """
        Perform multi-stage cryptographic mixing.
        
        Args:
            data: Input data bytes
            stages: Number of mixing stages
            
        Returns:
            Tuple of (mixed_entropy, final_hash)
        """
        current_data = data
        mixed_entropy = 0
        
        for stage in range(stages):
            # Compute hash
            hash_hex = self.compute_sha384(current_data)
            
            # Extract entropy
            entropy = self.extract_entropy(hash_hex, bit_offset=stage * 6)
            
            # XOR mix with accumulator
            mixed_entropy = self.xor_mix(mixed_entropy, entropy)
            
            # Prepare data for next stage
            current_data = hash_hex.encode('utf-8')
        
        # Update accumulator
        self.entropy_accumulator = self.xor_mix(
            self.entropy_accumulator, mixed_entropy
        )
        
        self.mix_count += 1
        self.history.append(data)
        
        # Keep history bounded
        if len(self.history) > 1000:
            self.history = self.history[-500:]
        
        final_hash = self.compute_sha384(current_data)
        
        return mixed_entropy, final_hash
    
    def mix_with_seed(self, data: bytes, seed: int) -> int:
        """Mix data with a seed value"""
        # Combine data and seed
        combined = data + seed.to_bytes(8, byteorder='big')
        
        # Compute hash
        hash_hex = self.compute_sha384(combined)
        
        # Extract and mix entropy
        entropy = self.extract_entropy(hash_hex)
        
        return self.xor_mix(entropy, seed & self.ENTROPY_MASK)
    
    def get_statistics(self) -> dict:
        """Get mixer statistics"""
        return {
            "mix_count": self.mix_count,
            "entropy_accumulator": self.entropy_accumulator,
            "history_size": len(self.history),
        }
    
    def reset(self):
        """Reset mixer state"""
        self.entropy_accumulator = 0
        self.mix_count = 0
        self.history = []
