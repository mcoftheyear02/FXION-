"""
Bandwidth Manager
Manages LAN and network bandwidth allocation for CCX and WayLink operations.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class BandwidthPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class BandwidthChannel:
    """Represents a bandwidth channel"""
    channel_id: int
    name: str
    total_bandwidth_gbps: float
    allocated_bandwidth_gbps: float
    current_usage_gbps: float
    active_connections: int


class BandwidthManager:
    """
    Network bandwidth manager for LAN and CCX operations.
    
    Features:
    - 100 Gbps base LAN bandwidth
    - Dynamic allocation across channels
    - Priority-based scheduling
    - Real-time utilization monitoring
    """
    
    BASE_LAN_BANDWIDTH_GBPS = 100.0
    MAX_CHANNELS = 16
    
    def __init__(self):
        self.channels: Dict[int, BandwidthChannel] = {}
        self.total_allocated = 0.0
        self.priority_queues: Dict[BandwidthPriority, List[int]] = {
            p: [] for p in BandwidthPriority
        }
        self._initialize_default_channels()
    
    def _initialize_default_channels(self):
        """Initialize default bandwidth channels"""
        default_channels = [
            (0, "CCX_North_South", 25.0),
            (1, "CCX_East_West", 25.0),
            (2, "WayLink_L1_L3", 15.0),
            (3, "WayLink_L4_L6", 15.0),
            (4, "GPU_VRAM", 10.0),
            (5, "CPU_Cache", 10.0),
        ]
        
        for channel_id, name, bandwidth in default_channels:
            self.create_channel(channel_id, name, bandwidth)
    
    def create_channel(self, channel_id: int, name: str, 
                       bandwidth_gbps: float) -> BandwidthChannel:
        """Create a new bandwidth channel"""
        if len(self.channels) >= self.MAX_CHANNELS:
            raise ValueError(f"Maximum channels ({self.MAX_CHANNELS}) reached")
        
        channel = BandwidthChannel(
            channel_id=channel_id,
            name=name,
            total_bandwidth_gbps=bandwidth_gbps,
            allocated_bandwidth_gbps=0.0,
            current_usage_gbps=0.0,
            active_connections=0
        )
        
        self.channels[channel_id] = channel
        return channel
    
    def allocate_bandwidth(self, channel_id: int, amount_gbps: float,
                           priority: BandwidthPriority = BandwidthPriority.NORMAL) -> bool:
        """
        Allocate bandwidth to a channel.
        
        Args:
            channel_id: Target channel ID
            amount_gbps: Amount to allocate
            priority: Allocation priority
            
        Returns:
            True if allocation successful
        """
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        
        # Check if enough bandwidth available
        available = self.BASE_LAN_BANDWIDTH_GBPS - self.total_allocated
        
        if amount_gbps > available:
            # Try to reclaim from lower priority channels
            reclaimed = self._reclaim_bandwidth(amount_gbps - available, priority)
            
            if reclaimed < (amount_gbps - available):
                return False
        
        # Perform allocation
        channel.allocated_bandwidth_gbps += amount_gbps
        self.total_allocated += amount_gbps
        
        # Add to priority queue
        self.priority_queues[priority].append(channel_id)
        
        return True
    
    def _reclaim_bandwidth(self, needed_gbps: float, 
                           priority: BandwidthPriority) -> float:
        """Reclaim bandwidth from lower priority channels"""
        reclaimed = 0.0
        
        # Iterate through lower priorities
        for p in BandwidthPriority:
            if p.value >= priority.value:
                break
            
            for channel_id in self.priority_queues[p]:
                if channel_id not in self.channels:
                    continue
                
                channel = self.channels[channel_id]
                
                # Reclaim up to 50% of allocated
                reclaimable = channel.allocated_bandwidth_gbps * 0.5
                
                if reclaimable > 0:
                    actual_reclaim = min(reclaimable, needed_gbps - reclaimed)
                    channel.allocated_bandwidth_gbps -= actual_reclaim
                    self.total_allocated -= actual_reclaim
                    reclaimed += actual_reclaim
                    
                    if reclaimed >= needed_gbps:
                        return reclaimed
        
        return reclaimed
    
    def release_bandwidth(self, channel_id: int, amount_gbps: float) -> bool:
        """Release allocated bandwidth from a channel"""
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        
        actual_release = min(amount_gbps, channel.allocated_bandwidth_gbps)
        channel.allocated_bandwidth_gbps -= actual_release
        self.total_allocated -= actual_release
        
        return True
    
    def update_usage(self, channel_id: int, usage_gbps: float) -> bool:
        """Update current usage for a channel"""
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        channel.current_usage_gbps = min(usage_gbps, channel.allocated_bandwidth_gbps)
        
        return True
    
    def get_utilization(self) -> Dict:
        """Get bandwidth utilization statistics"""
        channel_stats = {}
        
        for channel_id, channel in self.channels.items():
            utilization = (channel.current_usage_gbps / 
                          max(channel.total_bandwidth_gbps, 0.001))
            
            channel_stats[channel_id] = {
                "name": channel.name,
                "total_gbps": channel.total_bandwidth_gbps,
                "allocated_gbps": channel.allocated_bandwidth_gbps,
                "usage_gbps": channel.current_usage_gbps,
                "utilization": utilization,
                "connections": channel.active_connections,
            }
        
        return {
            "base_bandwidth_gbps": self.BASE_LAN_BANDWIDTH_GBPS,
            "total_allocated_gbps": self.total_allocated,
            "available_gbps": self.BASE_LAN_BANDWIDTH_GBPS - self.total_allocated,
            "allocation_ratio": self.total_allocated / self.BASE_LAN_BANDWIDTH_GBPS,
            "channels": channel_stats,
        }
    
    def get_available_bandwidth(self) -> float:
        """Get total available bandwidth"""
        return self.BASE_LAN_BANDWIDTH_GBPS - self.total_allocated
    
    def reset(self):
        """Reset bandwidth manager state"""
        for channel in self.channels.values():
            channel.allocated_bandwidth_gbps = 0.0
            channel.current_usage_gbps = 0.0
            channel.active_connections = 0
        
        self.total_allocated = 0.0
        
        for priority in self.priority_queues:
            self.priority_queues[priority] = []
