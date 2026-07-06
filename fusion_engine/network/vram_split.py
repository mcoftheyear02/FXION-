"""
VRAM Split Manager
Manages GPU/CPU VRAM split with 1:1 ratio and stability factor 0.625.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class MemoryType(Enum):
    GPU_VRAM = "gpu"
    CPU_VRAM = "cpu"
    SHARED = "shared"


@dataclass
class VRAMRegion:
    """Represents a VRAM region"""
    region_id: int
    memory_type: MemoryType
    size_mb: int
    allocated_mb: int
    way_count: int
    active: bool = True


class VRAMSplitManager:
    """
    VRAM split manager for GPU/CPU memory allocation.
    
    Features:
    - 50/50 GPU/CPU split (1:1 ratio)
    - Stability factor 0.625
    - Way-based allocation
    - Dynamic rebalancing
    """
    
    TOTAL_VRAM_MB = 16384  # 16 GB base
    GPU_CPU_RATIO = 1.0  # 1:1 ratio
    STABILITY_FACTOR = 0.625
    TOTAL_WAYS = 64  # L6 cache ways
    
    def __init__(self):
        self.regions: Dict[int, VRAMRegion] = {}
        self.gpu_allocated = 0
        self.cpu_allocated = 0
        self.region_counter = 0
        
        # Calculate split sizes
        self.gpu_total = int(self.TOTAL_VRAM_MB * 0.5 * self.STABILITY_FACTOR)
        self.cpu_total = int(self.TOTAL_VRAM_MB * 0.5 * self.STABILITY_FACTOR)
        
        # Initialize default regions
        self._initialize_regions()
    
    def _initialize_regions(self):
        """Initialize default VRAM regions"""
        # GPU regions (20 ways)
        gpu_ways = 20
        gpu_way_size = self.gpu_total // gpu_ways
        
        for i in range(gpu_ways):
            self.create_region(
                memory_type=MemoryType.GPU_VRAM,
                size_mb=gpu_way_size,
                way_count=1
            )
        
        # CPU regions (44 ways)
        cpu_ways = 44
        cpu_way_size = self.cpu_total // cpu_ways
        
        for i in range(cpu_ways):
            self.create_region(
                memory_type=MemoryType.CPU_VRAM,
                size_mb=cpu_way_size,
                way_count=1
            )
    
    def create_region(self, memory_type: MemoryType, 
                      size_mb: int, way_count: int = 1) -> VRAMRegion:
        """Create a new VRAM region"""
        self.region_counter += 1
        
        region = VRAMRegion(
            region_id=self.region_counter,
            memory_type=memory_type,
            size_mb=size_mb,
            allocated_mb=0,
            way_count=way_count,
            active=True
        )
        
        self.regions[self.region_counter] = region
        return region
    
    def allocate(self, region_id: int, amount_mb: int) -> bool:
        """
        Allocate memory from a region.
        
        Args:
            region_id: Target region ID
            amount_mb: Amount to allocate
            
        Returns:
            True if allocation successful
        """
        if region_id not in self.regions:
            return False
        
        region = self.regions[region_id]
        
        available = region.size_mb - region.allocated_mb
        
        if amount_mb > available:
            return False
        
        region.allocated_mb += amount_mb
        
        if region.memory_type == MemoryType.GPU_VRAM:
            self.gpu_allocated += amount_mb
        else:
            self.cpu_allocated += amount_mb
        
        return True
    
    def deallocate(self, region_id: int, amount_mb: int) -> bool:
        """Release allocated memory from a region"""
        if region_id not in self.regions:
            return False
        
        region = self.regions[region_id]
        
        actual_release = min(amount_mb, region.allocated_mb)
        region.allocated_mb -= actual_release
        
        if region.memory_type == MemoryType.GPU_VRAM:
            self.gpu_allocated -= actual_release
        else:
            self.cpu_allocated -= actual_release
        
        return True
    
    def get_split_ratio(self) -> Tuple[float, float]:
        """Get current GPU/CPU split ratio"""
        total_used = self.gpu_allocated + self.cpu_allocated
        
        if total_used == 0:
            return 0.5, 0.5
        
        gpu_ratio = self.gpu_allocated / total_used
        cpu_ratio = self.cpu_allocated / total_used
        
        return gpu_ratio, cpu_ratio
    
    def rebalance(self, target_ratio: float = 0.5):
        """
        Rebalance VRAM between GPU and CPU.
        
        Args:
            target_ratio: Target GPU ratio (0.0-1.0)
        """
        # Calculate ideal sizes
        ideal_gpu = int(self.TOTAL_VRAM_MB * target_ratio * self.STABILITY_FACTOR)
        ideal_cpu = int(self.TOTAL_VRAM_MB * (1 - target_ratio) * self.STABILITY_FACTOR)
        
        # Adjust region sizes (simplified - in real system would migrate data)
        gpu_regions = [r for r in self.regions.values() 
                      if r.memory_type == MemoryType.GPU_VRAM]
        cpu_regions = [r for r in self.regions.values() 
                      if r.memory_type == MemoryType.CPU_VRAM]
        
        if gpu_regions:
            new_gpu_way_size = ideal_gpu // len(gpu_regions)
            for region in gpu_regions:
                region.size_mb = new_gpu_way_size
        
        if cpu_regions:
            new_cpu_way_size = ideal_cpu // len(cpu_regions)
            for region in cpu_regions:
                region.size_mb = new_cpu_way_size
    
    def get_statistics(self) -> Dict:
        """Get VRAM split statistics"""
        gpu_regions = [r for r in self.regions.values() 
                      if r.memory_type == MemoryType.GPU_VRAM]
        cpu_regions = [r for r in self.regions.values() 
                      if r.memory_type == MemoryType.CPU_VRAM]
        
        gpu_total_size = sum(r.size_mb for r in gpu_regions)
        cpu_total_size = sum(r.size_mb for r in cpu_regions)
        
        gpu_ratio, cpu_ratio = self.get_split_ratio()
        
        return {
            "total_vram_mb": self.TOTAL_VRAM_MB,
            "stability_factor": self.STABILITY_FACTOR,
            "target_ratio": self.GPU_CPU_RATIO,
            "gpu_total_mb": gpu_total_size,
            "cpu_total_mb": cpu_total_size,
            "gpu_allocated_mb": self.gpu_allocated,
            "cpu_allocated_mb": self.cpu_allocated,
            "gpu_utilization": self.gpu_allocated / max(gpu_total_size, 1),
            "cpu_utilization": self.cpu_allocated / max(cpu_total_size, 1),
            "current_split_ratio": {
                "gpu": gpu_ratio,
                "cpu": cpu_ratio,
            },
            "gpu_regions": len(gpu_regions),
            "cpu_regions": len(cpu_regions),
            "total_ways": sum(r.way_count for r in self.regions.values()),
        }
    
    def reset(self):
        """Reset VRAM manager state"""
        for region in self.regions.values():
            region.allocated_mb = 0
        
        self.gpu_allocated = 0
        self.cpu_allocated = 0
