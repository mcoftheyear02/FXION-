"""
OMNITECH OMEGA v3.0 - RL-driven Quantization Optimizer
UCB1 Bandit Policy for GGUF Quantization Selection
"""

import json
import math
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ArmState:
    """State for a single quantization arm in the UCB1 bandit."""
    n_pulls: int = 0
    total_reward: float = 0.0
    rewards: List[float] = field(default_factory=list)
    
    @property
    def mean_reward(self) -> float:
        if self.n_pulls == 0:
            return float('inf')  # Encourage exploration of unvisited arms
        return self.total_reward / self.n_pulls
    
    def update(self, reward: float):
        self.n_pulls += 1
        self.total_reward += reward
        self.rewards.append(reward)


class UCB1Policy:
    """UCB1 (Upper Confidence Bound) policy for quantization selection."""
    
    QUANT_LEVELS = ['Q2_K', 'Q3_K', 'Q4_K_M', 'Q5_K_M', 'Q6_K', 'Q8_0']
    
    def __init__(self, state_file: str = '/tmp/ucb1_policy.json', 
                 exploration_param: float = 2.0):
        self.state_file = state_file
        self.exploration_param = exploration_param
        self.arms: Dict[str, ArmState] = {}
        self.total_pulls = 0
        self.history: List[Dict] = []
        
        # Load existing state if available
        self._load_state()
    
    def _load_state(self):
        """Load policy state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                self.total_pulls = data.get('total_pulls', 0)
                self.history = data.get('history', [])
                
                for level in self.QUANT_LEVELS:
                    arm_data = data.get('arms', {}).get(level, {})
                    self.arms[level] = ArmState(
                        n_pulls=arm_data.get('n_pulls', 0),
                        total_reward=arm_data.get('total_reward', 0.0),
                        rewards=arm_data.get('rewards', [])
                    )
            except Exception as e:
                print(f"Warning: Could not load policy state: {e}")
                self._initialize_arms()
        else:
            self._initialize_arms()
    
    def _initialize_arms(self):
        """Initialize all quantization arms."""
        for level in self.QUANT_LEVELS:
            self.arms[level] = ArmState()
    
    def _save_state(self):
        """Save policy state to disk."""
        data = {
            'total_pulls': self.total_pulls,
            'history': self.history[-1000:],  # Keep last 1000 entries
            'arms': {
                level: {
                    'n_pulls': arm.n_pulls,
                    'total_reward': arm.total_reward,
                    'rewards': arm.rewards[-100:]  # Keep last 100 rewards
                }
                for level, arm in self.arms.items()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def select_arm(self) -> str:
        """Select next quantization level using UCB1 algorithm."""
        best_ucb = -float('inf')
        best_level = self.QUANT_LEVELS[0]
        
        for level in self.QUANT_LEVELS:
            arm = self.arms[level]
            
            # UCB1 formula: mean + c * sqrt(ln(n_total) / n_arm)
            if arm.n_pulls == 0:
                ucb_value = float('inf')  # Force exploration of unvisited arms
            else:
                exploitation = arm.mean_reward
                exploration = self.exploration_param * math.sqrt(
                    math.log(max(1, self.total_pulls)) / arm.n_pulls
                )
                ucb_value = exploitation + exploration
            
            if ucb_value > best_ucb:
                best_ucb = ucb_value
                best_level = level
        
        return best_level
    
    def update(self, quant_level: str, reward: float, 
               tps: float, accuracy: float, size_mb: float):
        """Update policy with observed reward."""
        if quant_level not in self.arms:
            raise ValueError(f"Unknown quantization level: {quant_level}")
        
        # Update arm statistics
        self.arms[quant_level].update(reward)
        self.total_pulls += 1
        
        # Record history
        entry = {
            'timestamp': datetime.now().isoformat(),
            'quant_level': quant_level,
            'reward': reward,
            'tps': tps,
            'accuracy': accuracy,
            'size_mb': size_mb,
            'n_pulls': self.arms[quant_level].n_pulls
        }
        self.history.append(entry)
        
        # Persist state
        self._save_state()
    
    def get_best_quant(self) -> str:
        """Get the quantization level with highest mean reward."""
        best_mean = -float('inf')
        best_level = self.QUANT_LEVELS[0]
        
        for level, arm in self.arms.items():
            if arm.n_pulls > 0 and arm.mean_reward > best_mean:
                best_mean = arm.mean_reward
                best_level = level
        
        return best_level
    
    def get_stats(self) -> Dict:
        """Get current policy statistics."""
        return {
            'total_pulls': self.total_pulls,
            'best_quant': self.get_best_quant(),
            'arms': {
                level: {
                    'n_pulls': arm.n_pulls,
                    'mean_reward': arm.mean_reward if arm.n_pulls > 0 else None,
                    'total_reward': arm.total_reward
                }
                for level, arm in self.arms.items()
            },
            'recent_history': self.history[-10:]
        }


if __name__ == '__main__':
    # Test the policy
    policy = UCB1Policy()
    
    print("Initial arm selection:")
    for i in range(10):
        selected = policy.select_arm()
        print(f"  Iteration {i+1}: Selected {selected}")
        # Simulate reward
        reward = 0.5 + (0.1 * hash(selected) % 10) / 10
        policy.update(selected, reward, 50.0, 0.95, 1000.0)
    
    print("\nPolicy statistics:")
    stats = policy.get_stats()
    print(json.dumps(stats, indent=2))
