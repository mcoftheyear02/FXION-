"""
OMNITECH OMEGA v3.0 - Security AI for Anomaly Detection
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
import statistics


class SecurityAI:
    """AI-powered anomaly detection and alerting system."""
    
    def __init__(self, state_file: str = '/tmp/security_ai.json'):
        self.state_file = state_file
        self.alerts: List[Dict] = []
        self.metrics_history: Dict[str, deque] = {
            'tps': deque(maxlen=100),
            'accuracy': deque(maxlen=100),
            'reward': deque(maxlen=100),
            'iteration_time': deque(maxlen=100)
        }
        self.baseline_stats: Dict[str, Dict] = {}
        self.anomaly_threshold = 2.5  # Standard deviations
        
        # Load existing state
        self._load_state()
    
    def _load_state(self):
        """Load security AI state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                self.alerts = data.get('alerts', [])[-100:]  # Keep last 100
                self.baseline_stats = data.get('baseline_stats', {})
            except Exception as e:
                print(f"Warning: Could not load security state: {e}")
    
    def _save_state(self):
        """Save security AI state to disk."""
        data = {
            'alerts': self.alerts[-100:],
            'baseline_stats': self.baseline_stats,
            'last_update': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_metric(self, metric_name: str, value: float):
        """Record a metric value."""
        if metric_name in self.metrics_history:
            self.metrics_history[metric_name].append(value)
            
            # Update baseline if we have enough data
            if len(self.metrics_history[metric_name]) >= 10:
                self._update_baseline(metric_name)
    
    def _update_baseline(self, metric_name: str):
        """Update baseline statistics for a metric."""
        values = list(self.metrics_history[metric_name])
        self.baseline_stats[metric_name] = {
            'mean': statistics.mean(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'updated_at': datetime.now().isoformat()
        }
        self._save_state()
    
    def detect_anomaly(self, metric_name: str, value: float) -> Optional[Dict]:
        """Detect if a value is anomalous."""
        if metric_name not in self.baseline_stats:
            return None
        
        baseline = self.baseline_stats[metric_name]
        if baseline['stdev'] == 0:
            return None
        
        # Calculate z-score
        z_score = abs(value - baseline['mean']) / baseline['stdev']
        
        if z_score > self.anomaly_threshold:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'anomaly',
                'metric': metric_name,
                'value': value,
                'baseline_mean': baseline['mean'],
                'baseline_stdev': baseline['stdev'],
                'z_score': z_score,
                'severity': 'high' if z_score > 4 else 'medium'
            }
            self.alerts.append(alert)
            self._save_state()
            return alert
        
        return None
    
    def check_rate_limit(self, requests_per_minute: int, limit: int = 100) -> bool:
        """Check if request rate exceeds limit."""
        if requests_per_minute > limit:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'rate_limit_exceeded',
                'requests_per_minute': requests_per_minute,
                'limit': limit,
                'severity': 'high'
            }
            self.alerts.append(alert)
            self._save_state()
            return False
        return True
    
    def detect_quantization_attack(self, quant_levels: List[str], window: int = 10) -> Optional[Dict]:
        """Detect if someone is repeatedly requesting the same quantization (potential attack)."""
        if len(quant_levels) < window:
            return None
        
        recent = quant_levels[-window:]
        most_common = max(set(recent), key=recent.count)
        count = recent.count(most_common)
        
        # If >80% of recent requests are for the same quantization
        if count / window > 0.8:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'suspicious_pattern',
                'description': f'Repeated requests for {most_common}',
                'count': count,
                'window': window,
                'severity': 'medium'
            }
            self.alerts.append(alert)
            self._save_state()
            return alert
        
        return None
    
    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts."""
        return self.alerts[-limit:]
    
    def get_health_status(self) -> Dict:
        """Get overall security health status."""
        recent_alerts = [a for a in self.alerts 
                        if datetime.fromisoformat(a['timestamp']) > 
                        datetime.now().replace(minute=datetime.now().minute - 5)]
        
        high_severity = sum(1 for a in recent_alerts if a.get('severity') == 'high')
        
        status = 'healthy'
        if high_severity > 0:
            status = 'critical'
        elif len(recent_alerts) > 5:
            status = 'warning'
        
        return {
            'status': status,
            'total_alerts': len(self.alerts),
            'recent_alerts': len(recent_alerts),
            'high_severity_count': high_severity,
            'baselines_tracked': len(self.baseline_stats),
            'last_update': datetime.now().isoformat()
        }
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []
        self._save_state()


if __name__ == '__main__':
    # Test the security AI
    security = SecurityAI()
    
    print("Testing anomaly detection...")
    
    # Record some normal values
    for i in range(20):
        security.record_metric('tps', 50 + (i % 5))
        security.record_metric('accuracy', 0.85 + (i % 10) * 0.01)
    
    # Try an anomalous value
    anomaly = security.detect_anomaly('tps', 200.0)
    if anomaly:
        print(f"Anomaly detected: {json.dumps(anomaly, indent=2)}")
    
    # Get health status
    print("\nHealth Status:")
    print(json.dumps(security.get_health_status(), indent=2))
    
    # Get alerts
    print("\nRecent Alerts:")
    print(json.dumps(security.get_alerts(), indent=2))
