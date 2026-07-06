"""
CCX Optimizer - Complex Cache eXchange optimization for 6x6 CCX IQ4 networks
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random


@dataclass
class CCXNode:
    """Represents a CCX (Core Complex) node"""
    node_id: int
    core_count: int
    cache_ways: int
    active: bool = True
    load_factor: float = 0.0
    iq_depth: int = 4  # Instruction Queue depth


@dataclass
class CCXLink:
    """Represents a link between CCX nodes"""
    source_node: int
    dest_node: int
    link_id: int
    bandwidth_gbps: float
    latency_ns: float
    utilization: float = 0.0
    packet_count: int = 0


@dataclass
class CCXRequest:
    """Represents a CCX network request"""
    request_id: int
    source_node: int
    dest_node: int
    data_size: int
    priority: int
    timestamp: float
    completed: bool = False
    latency_ns: float = 0.0


class CCXOptimizer:
    """
    CCX Network Optimizer for 6x6 topology with IQ4 scheduling.
    
    Features:
    - 6x6 CCX node matrix (36 nodes)
    - IQ4 instruction queue depth
    - 5-way parallel links per node pair
    - LAN bandwidth optimization (100 Gbps base)
    - Predictive load balancing
    """
    
    GRID_SIZE = 6  # 6x6 grid
    IQ_DEPTH = 4   # Instruction Queue depth
    BASE_BANDWIDTH_GBPS = 100.0
    LINKS_PER_PAIR = 5
    
    def __init__(self):
        self.ccx_nodes: Dict[int, CCXNode] = {}
        self.ccx_links: List[CCXLink] = []
        self.request_queue: List[CCXRequest] = []
        self.completed_requests: List[CCXRequest] = []
        self.request_counter = 0
        
        self._initialize_ccx_grid()
        self._build_ccx_links()
    
    def _initialize_ccx_grid(self):
        """Initialize 6x6 CCX grid"""
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                node_id = row * self.GRID_SIZE + col
                
                node = CCXNode(
                    node_id=node_id,
                    core_count=8,  # 8 cores per CCX
                    cache_ways=64,  # L6 cache ways
                    active=True,
                    iq_depth=self.IQ_DEPTH
                )
                
                self.ccx_nodes[node_id] = node
    
    def _build_ccx_links(self):
        """Build links between adjacent CCX nodes"""
        link_id = 0
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                node_id = row * self.GRID_SIZE + col
                
                # Connect to right neighbor
                if col < self.GRID_SIZE - 1:
                    right_node = node_id + 1
                    
                    for i in range(self.LINKS_PER_PAIR):
                        link = CCXLink(
                            source_node=node_id,
                            dest_node=right_node,
                            link_id=link_id,
                            bandwidth_gbps=self.BASE_BANDWIDTH_GBPS / (i + 1),
                            latency_ns=10.0 + i * 2.0
                        )
                        self.ccx_links.append(link)
                        link_id += 1
                
                # Connect to bottom neighbor
                if row < self.GRID_SIZE - 1:
                    bottom_node = node_id + self.GRID_SIZE
                    
                    for i in range(self.LINKS_PER_PAIR):
                        link = CCXLink(
                            source_node=node_id,
                            dest_node=bottom_node,
                            link_id=link_id,
                            bandwidth_gbps=self.BASE_BANDWIDTH_GBPS / (i + 1),
                            latency_ns=15.0 + i * 3.0
                        )
                        self.ccx_links.append(link)
                        link_id += 1
    
    def submit_request(self, source_node: int, dest_node: int, 
                       data_size: int, priority: int = 0) -> CCXRequest:
        """
        Submit a CCX network request.
        
        Args:
            source_node: Source CCX node ID
            dest_node: Destination CCX node ID
            data_size: Size of data to transfer (bytes)
            priority: Request priority (0-7)
            
        Returns:
            CCXRequest object
        """
        self.request_counter += 1
        
        request = CCXRequest(
            request_id=self.request_counter,
            source_node=source_node,
            dest_node=dest_node,
            data_size=data_size,
            priority=priority,
            timestamp=self._get_timestamp()
        )
        
        # Add to queue with IQ depth consideration
        source_node_obj = self.ccx_nodes.get(source_node)
        if source_node_obj and len(self.request_queue) < source_node_obj.iq_depth * 10:
            self.request_queue.append(request)
        
        return request
    
    def process_requests(self) -> List[CCXRequest]:
        """Process pending requests through the CCX network"""
        processed = []
        
        # Sort by priority
        self.request_queue.sort(key=lambda r: (-r.priority, r.timestamp))
        
        # Process up to IQ_DEPTH requests per cycle
        batch_size = min(len(self.request_queue), self.IQ_DEPTH * 6)
        
        for i in range(batch_size):
            if not self.request_queue:
                break
            
            request = self.request_queue.pop(0)
            
            # Find optimal path
            path = self._find_optimal_path(request.source_node, request.dest_node)
            
            if path:
                # Calculate latency
                total_latency = self._calculate_path_latency(path, request.data_size)
                
                request.latency_ns = total_latency
                request.completed = True
                
                # Update link utilization
                self._update_link_utilization(path, request.data_size)
                
                processed.append(request)
                self.completed_requests.append(request)
        
        return processed
    
    def _find_optimal_path(self, source: int, dest: int) -> List[int]:
        """Find optimal path between source and destination nodes"""
        if source == dest:
            return [source]
        
        # Simple Manhattan routing for grid topology
        src_row, src_col = divmod(source, self.GRID_SIZE)
        dst_row, dst_col = divmod(dest, self.GRID_SIZE)
        
        path = [source]
        current = source
        current_row, current_col = src_row, src_col
        
        # Move horizontally first
        while current_col != dst_col:
            if current_col < dst_col:
                next_node = current + 1
                current_col += 1
            else:
                next_node = current - 1
                current_col -= 1
            
            path.append(next_node)
            current = next_node
        
        # Then move vertically
        while current_row != dst_row:
            if current_row < dst_row:
                next_node = current + self.GRID_SIZE
                current_row += 1
            else:
                next_node = current - self.GRID_SIZE
                current_row -= 1
            
            path.append(next_node)
            current = next_node
        
        return path
    
    def _calculate_path_latency(self, path: List[int], 
                                data_size: int) -> float:
        """Calculate total latency for a path"""
        if len(path) <= 1:
            return 0.0
        
        total_latency = 0.0
        
        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            
            # Find best link for this hop
            best_latency = float('inf')
            
            for link in self.ccx_links:
                if link.source_node == src and link.dest_node == dst:
                    # Calculate transmission latency
                    transmit_time = (data_size * 8) / (link.bandwidth_gbps * 1e9) * 1e9
                    total_hop_latency = link.latency_ns + transmit_time * (1 + link.utilization)
                    
                    if total_hop_latency < best_latency:
                        best_latency = total_hop_latency
            
            if best_latency < float('inf'):
                total_latency += best_latency
            else:
                total_latency += 20.0  # Default latency if no link found
        
        return total_latency
    
    def _update_link_utilization(self, path: List[int], data_size: int):
        """Update link utilization after a transfer"""
        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            
            for link in self.ccx_links:
                if link.source_node == src and link.dest_node == dst:
                    link.packet_count += 1
                    link.utilization = min(1.0, link.utilization + 0.01)
                    break
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.perf_counter()
    
    def get_network_statistics(self) -> Dict:
        """Get CCX network statistics"""
        total_bandwidth = sum(link.bandwidth_gbps for link in self.ccx_links)
        avg_utilization = (sum(link.utilization for link in self.ccx_links) / 
                          max(len(self.ccx_links), 1))
        
        completed_count = len(self.completed_requests)
        total_latency = sum(r.latency_ns for r in self.completed_requests)
        avg_latency = total_latency / max(completed_count, 1)
        
        # Node load distribution
        node_loads = {node_id: node.load_factor 
                     for node_id, node in self.ccx_nodes.items()}
        
        return {
            "total_nodes": len(self.ccx_nodes),
            "grid_size": f"{self.GRID_SIZE}x{self.GRID_SIZE}",
            "total_links": len(self.ccx_links),
            "links_per_pair": self.LINKS_PER_PAIR,
            "iq_depth": self.IQ_DEPTH,
            "total_bandwidth_gbps": total_bandwidth,
            "average_link_utilization": avg_utilization,
            "pending_requests": len(self.request_queue),
            "completed_requests": completed_count,
            "average_latency_ns": avg_latency,
            "node_load_distribution": node_loads,
        }
    
    def optimize_load_balance(self):
        """Perform load balancing across CCX nodes"""
        if not self.ccx_nodes:
            return
        
        # Calculate average load
        loads = [node.load_factor for node in self.ccx_nodes.values()]
        avg_load = sum(loads) / len(loads)
        
        # Redistribute load
        for node in self.ccx_nodes.values():
            if node.load_factor > avg_load * 1.2:
                # Overloaded - reduce load
                node.load_factor = avg_load * 1.1
            elif node.load_factor < avg_load * 0.8:
                # Underloaded - increase load
                node.load_factor = avg_load * 0.9
    
    def reset(self):
        """Reset CCX optimizer state"""
        for node in self.ccx_nodes.values():
            node.load_factor = 0.0
        
        for link in self.ccx_links:
            link.utilization = 0.0
            link.packet_count = 0
        
        self.request_queue = []
        self.completed_requests = []
        self.request_counter = 0
