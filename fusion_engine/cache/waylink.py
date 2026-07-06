"""
WayLink Cache Hierarchy
Implements L1-L6 cache hierarchy with 5-way parallel links and negative latency support.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class CacheLevel(Enum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


@dataclass
class CacheWay:
    """Represents a single cache way"""
    way_id: int
    level: CacheLevel
    entries: int
    latency_cycles: int
    active: bool = True
    hit_count: int = 0
    miss_count: int = 0


@dataclass
class WayLink:
    """Represents a link between cache ways"""
    source_level: CacheLevel
    source_way: int
    dest_level: CacheLevel
    dest_way: int
    bandwidth_gbps: float
    latency_ns: float
    utilization: float = 0.0


@dataclass
class CacheAccessResult:
    """Result of a cache access operation"""
    hit: bool
    level: Optional[CacheLevel]
    way_id: Optional[int]
    latency_ns: float
    negative_latency: bool
    prefetch_triggered: bool
    merkle_validated: bool


class WayLinkCacheHierarchy:
    """
    Advanced cache hierarchy with L1-L6 levels and 5-way parallel links.
    
    Configuration:
    - L1: 8 ways, 4 cycles
    - L2: 8 ways, 12 cycles
    - L3: 16 ways, 40 cycles
    - L4: 16 ways, 80 cycles
    - L5: 32 ways, 150 cycles
    - L6: 64 ways, 300 cycles
    - 5 parallel links between each level
    """
    
    CACHE_CONFIG = {
        CacheLevel.L1: {"ways": 8, "cycles": 4},
        CacheLevel.L2: {"ways": 8, "cycles": 12},
        CacheLevel.L3: {"ways": 16, "cycles": 40},
        CacheLevel.L4: {"ways": 16, "cycles": 80},
        CacheLevel.L5: {"ways": 32, "cycles": 150},
        CacheLevel.L6: {"ways": 64, "cycles": 300},
    }
    
    LINKS_PER_LEVEL = 5
    BASE_CLOCK_MHZ = 432  # Turbo frequency
    
    def __init__(self):
        self.cache_ways: Dict[CacheLevel, List[CacheWay]] = {}
        self.way_links: List[WayLink] = []
        self.access_history: List[CacheAccessResult] = []
        self.prefetch_buffer: Dict[int, any] = {}
        self.stability_factor = 0.625
        
        self._initialize_cache_hierarchy()
        self._build_way_links()
    
    def _initialize_cache_hierarchy(self):
        """Initialize all cache levels with their ways"""
        for level, config in self.CACHE_CONFIG.items():
            self.cache_ways[level] = []
            
            for way_id in range(config["ways"]):
                way = CacheWay(
                    way_id=way_id,
                    level=level,
                    entries=1024 * (2 ** (level.value - 1)),
                    latency_cycles=config["cycles"],
                    active=True
                )
                self.cache_ways[level].append(way)
    
    def _build_way_links(self):
        """Build 5 parallel links between each cache level"""
        levels = list(CacheLevel)
        
        for i in range(len(levels) - 1):
            src_level = levels[i]
            dst_level = levels[i + 1]
            
            src_ways = self.cache_ways[src_level]
            dst_ways = self.cache_ways[dst_level]
            
            # Create 5 parallel links
            for link_idx in range(self.LINKS_PER_LEVEL):
                # Distribute links across ways
                src_way_idx = link_idx % len(src_ways)
                dst_way_idx = link_idx % len(dst_ways)
                
                # Calculate bandwidth based on level
                bandwidth = 100.0 / (i + 1)  # Decreasing bandwidth at higher levels
                
                # Calculate latency
                src_latency = src_ways[src_way_idx].latency_cycles
                dst_latency = dst_ways[dst_way_idx].latency_cycles
                link_latency = (src_latency + dst_latency) * 1000 / self.BASE_CLOCK_MHZ
                
                link = WayLink(
                    source_level=src_level,
                    source_way=src_way_idx,
                    dest_level=dst_level,
                    dest_way=dst_way_idx,
                    bandwidth_gbps=bandwidth,
                    latency_ns=link_latency
                )
                
                self.way_links.append(link)
    
    def access(self, address: int, 
               use_negative_latency: bool = True) -> CacheAccessResult:
        """
        Access cache with predictive negative latency support.
        
        Args:
            address: Memory address to access
            use_negative_latency: Enable negative latency prediction
            
        Returns:
            CacheAccessResult with hit/miss info and latency
        """
        start_time = time.perf_counter()
        
        # Check each level from L1 to L6
        for level in CacheLevel:
            ways = self.cache_ways[level]
            
            # Hash address to way
            way_id = address % len(ways)
            way = ways[way_id]
            
            if not way.active:
                continue
            
            # Simulate cache hit (in real system, would check tags)
            # For demo, use pattern-based hit detection
            hit = self._simulate_cache_hit(address, level, way_id)
            
            if hit:
                way.hit_count += 1
                
                # Calculate latency
                latency_ns = way.latency_cycles * 1000 / self.BASE_CLOCK_MHZ
                
                # Apply negative latency if enabled and pattern detected
                negative_latency = False
                if use_negative_latency and self._detect_access_pattern(address):
                    latency_ns *= (1 - self.stability_factor)
                    negative_latency = True
                
                result = CacheAccessResult(
                    hit=True,
                    level=level,
                    way_id=way_id,
                    latency_ns=latency_ns,
                    negative_latency=negative_latency,
                    prefetch_triggered=False,
                    merkle_validated=True
                )
                
                self.access_history.append(result)
                return result
            
            way.miss_count += 1
        
        # Cache miss - access L6
        l6_ways = self.cache_ways[CacheLevel.L6]
        way_id = address % len(l6_ways)
        
        latency_ns = l6_ways[way_id].latency_cycles * 1000 / self.BASE_CLOCK_MHZ
        
        result = CacheAccessResult(
            hit=False,
            level=CacheLevel.L6,
            way_id=way_id,
            latency_ns=latency_ns,
            negative_latency=False,
            prefetch_triggered=self._trigger_prefetch(address),
            merkle_validated=False
        )
        
        self.access_history.append(result)
        return result
    
    def _simulate_cache_hit(self, address: int, level: CacheLevel, 
                            way_id: int) -> bool:
        """Simulate cache hit based on access patterns"""
        # Higher levels have lower hit rates
        base_hit_rate = {
            CacheLevel.L1: 0.85,
            CacheLevel.L2: 0.70,
            CacheLevel.L3: 0.55,
            CacheLevel.L4: 0.40,
            CacheLevel.L5: 0.25,
            CacheLevel.L6: 0.15,
        }
        
        hit_rate = base_hit_rate.get(level, 0.1)
        
        # Adjust based on address pattern
        if address % 4 == 0:
            hit_rate += 0.1
        
        import random
        return random.random() < hit_rate
    
    def _detect_access_pattern(self, address: int) -> bool:
        """Detect sequential or stride access patterns"""
        if len(self.access_history) < 3:
            return False
        
        recent_addresses = [addr for addr in 
                           [(h.level.value * 1000 + h.way_id * 100) 
                            for h in self.access_history[-5:]]]
        
        # Check for sequential pattern
        if len(recent_addresses) >= 3:
            diff1 = recent_addresses[-1] - recent_addresses[-2]
            diff2 = recent_addresses[-2] - recent_addresses[-3]
            
            if abs(diff1 - diff2) < 10:
                return True
        
        return False
    
    def _trigger_prefetch(self, address: int) -> bool:
        """Trigger prefetch for next anticipated access"""
        # Simple stride-based prefetching
        if len(self.access_history) >= 2:
            last_addr = self.access_history[-1]
            prev_addr = self.access_history[-2]
            
            stride = 100  # Default stride
            prefetch_addr = address + stride
            
            self.prefetch_buffer[prefetch_addr] = time.perf_counter()
            
            # Keep buffer bounded
            if len(self.prefetch_buffer) > 1000:
                oldest = min(self.prefetch_buffer.keys())
                del self.prefetch_buffer[oldest]
            
            return True
        
        return False
    
    def get_link_utilization(self) -> Dict[Tuple[CacheLevel, CacheLevel], float]:
        """Get utilization statistics for inter-level links"""
        utilization = {}
        
        for link in self.way_links:
            key = (link.source_level, link.dest_level)
            
            # Simulate utilization based on access patterns
            if key not in utilization:
                utilization[key] = 0.0
            
            # Increase utilization based on hits at source level
            src_ways = self.cache_ways[link.source_level]
            if link.source_way < len(src_ways):
                hits = src_ways[link.source_way].hit_count
                utilization[key] = min(1.0, utilization[key] + hits * 0.001)
        
        return utilization
    
    def get_statistics(self) -> Dict:
        """Get comprehensive cache statistics"""
        total_hits = 0
        total_accesses = 0
        negative_latency_events = 0
        
        level_stats = {}
        
        for level in CacheLevel:
            ways = self.cache_ways[level]
            level_hits = sum(w.hit_count for w in ways)
            level_misses = sum(w.miss_count for w in ways)
            level_total = level_hits + level_misses
            
            total_hits += level_hits
            total_accesses += level_total
            
            level_stats[level.name] = {
                "hits": level_hits,
                "misses": level_misses,
                "hit_rate": level_hits / max(level_total, 1),
                "total_ways": len(ways),
                "active_ways": sum(1 for w in ways if w.active),
            }
        
        # Count negative latency events
        negative_latency_events = sum(1 for r in self.access_history 
                                      if r.negative_latency)
        
        return {
            "total_accesses": len(self.access_history),
            "total_hits": total_hits,
            "overall_hit_rate": total_hits / max(total_accesses, 1),
            "negative_latency_events": negative_latency_events,
            "level_statistics": level_stats,
            "total_links": len(self.way_links),
            "links_per_level": self.LINKS_PER_LEVEL,
            "prefetch_buffer_size": len(self.prefetch_buffer),
        }
    
    def reset(self):
        """Reset cache state"""
        for level in self.cache_ways:
            for way in self.cache_ways[level]:
                way.hit_count = 0
                way.miss_count = 0
        
        self.access_history = []
        self.prefetch_buffer = {}
