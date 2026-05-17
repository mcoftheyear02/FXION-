"""
OMNITECH OMEGA v3.0 - Flask REST API and Live Dashboard
"""

import os
import json
import sys
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.policy import UCB1Policy
except ImportError:
    UCB1Policy = None

app = Flask(__name__)

# Initialize policy
policy = None
if UCB1Policy:
    try:
        policy = UCB1Policy()
    except Exception as e:
        print(f"Warning: Could not initialize policy: {e}")


# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ OMNITECH OMEGA v3.0 - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #0f3460;
            margin-bottom: 30px;
        }
        h1 { 
            font-size: 2.5em; 
            color: #e94560;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
        }
        .subtitle { color: #888; margin-top: 10px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        .card h2 {
            color: #0f3460;
            background: #e94560;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1.2em;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stat:last-child { border-bottom: none; }
        .stat-label { color: #888; }
        .stat-value { 
            font-weight: bold; 
            color: #00d9ff;
            font-size: 1.1em;
        }
        .best-quant {
            font-size: 2em;
            color: #00ff88;
            text-align: center;
            padding: 20px;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 10px;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        th {
            background: rgba(233, 69, 96, 0.2);
            color: #e94560;
        }
        tr:hover { background: rgba(255, 255, 255, 0.05); }
        .refresh-btn {
            background: #e94560;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            background: #ff6b6b;
            transform: translateY(-2px);
        }
        .auto-refresh {
            text-align: center;
            margin-top: 20px;
            color: #888;
        }
        .progress-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #e94560, #00d9ff);
            height: 100%;
            transition: width 0.5s;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ OMNITECH OMEGA v3.0</h1>
            <p class="subtitle">Autonomous AI Quantization Engine</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2>📊 System Status</h2>
                <div id="status-content">Loading...</div>
            </div>
            
            <div class="card">
                <h2>🎯 Best Quantization</h2>
                <div id="best-quant" class="best-quant">-</div>
                <div id="best-stats"></div>
            </div>
            
            <div class="card">
                <h2>🎲 Policy Arms</h2>
                <table id="arms-table">
                    <thead>
                        <tr>
                            <th>Level</th>
                            <th>Pulls</th>
                            <th>Mean Reward</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Recent History</h2>
            <table id="history-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Quant</th>
                        <th>Reward</th>
                        <th>TPS</th>
                        <th>Accuracy</th>
                        <th>Size (MB)</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            <p class="auto-refresh">Auto-refreshing every 5 seconds</p>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                // Load status
                const statusRes = await fetch('/api/status');
                const status = await statusRes.json();
                document.getElementById('status-content').innerHTML = `
                    <div class="stat"><span class="stat-label">Total Iterations:</span><span class="stat-value">${status.total_pulls || 0}</span></div>
                    <div class="stat"><span class="stat-label">Policy State:</span><span class="stat-value">${status.policy_loaded ? 'Loaded' : 'Not Loaded'}</span></div>
                    <div class="stat"><span class="stat-label">Last Update:</span><span class="stat-value">${status.last_update || 'N/A'}</span></div>
                `;
                
                // Load best quant
                const policyRes = await fetch('/api/policy');
                const policyData = await policyRes.json();
                
                if (policyData.best_quant) {
                    document.getElementById('best-quant').textContent = policyData.best_quant;
                    
                    const bestArm = policyData.arms[policyData.best_quant];
                    document.getElementById('best-stats').innerHTML = `
                        <div class="stat"><span class="stat-label">Pulls:</span><span class="stat-value">${bestArm?.n_pulls || 0}</span></div>
                        <div class="stat"><span class="stat-label">Mean Reward:</span><span class="stat-value">${bestArm?.mean_reward?.toFixed(4) || 'N/A'}</span></div>
                    `;
                }
                
                // Load arms table
                const tbody = document.querySelector('#arms-table tbody');
                tbody.innerHTML = '';
                for (const [level, arm] of Object.entries(policyData.arms || {})) {
                    const row = `<tr>
                        <td>${level}</td>
                        <td>${arm.n_pulls || 0}</td>
                        <td>${arm.mean_reward !== null ? arm.mean_reward.toFixed(4) : 'N/A'}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                }
                
                // Load history
                const histRes = await fetch('/api/history');
                const history = await histRes.json();
                
                const histBody = document.querySelector('#history-table tbody');
                histBody.innerHTML = '';
                for (const entry of history) {
                    const row = `<tr>
                        <td>${entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : 'N/A'}</td>
                        <td>${entry.quant_level}</td>
                        <td>${entry.reward?.toFixed(4) || 'N/A'}</td>
                        <td>${entry.tps?.toFixed(2) || 'N/A'}</td>
                        <td>${entry.accuracy?.toFixed(4) || 'N/A'}</td>
                        <td>${entry.size_mb?.toFixed(2) || 'N/A'}</td>
                    </tr>`;
                    histBody.innerHTML += row;
                }
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        // Initial load
        loadData();
        
        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Serve the live dashboard."""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def api_status():
    """Get system health status."""
    status = {
        'timestamp': datetime.now().isoformat(),
        'total_pulls': policy.total_pulls if policy else 0,
        'policy_loaded': policy is not None,
        'last_update': None
    }
    
    if policy and policy.history:
        status['last_update'] = policy.history[-1].get('timestamp')
    
    return jsonify(status)


@app.route('/api/policy')
def api_policy():
    """Get UCB1 policy state."""
    if not policy:
        return jsonify({'error': 'Policy not loaded'})
    
    return jsonify(policy.get_stats())


@app.route('/api/history')
def api_history():
    """Get last 100 RL iterations."""
    if not policy:
        return jsonify([])
    
    # Return last 100 entries
    return jsonify(policy.history[-100:])


@app.route('/quantum')
def quantum_dashboard():
    """Serve the Quantum Genesis IQ999+ Dashboard"""
    return send_from_directory('.', 'quantum_dashboard.html')

@app.route('/cyberpunk')
def cyberpunk_dashboard():
    """Serve the Cyberpunk Dashboard"""
    return send_from_directory('.', 'cyberpunk_dashboard.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'redis': 'mock',  # Would check real Redis in production
        'policy': 'loaded' if policy else 'not_loaded'
    })


if __name__ == '__main__':
    print("Starting OMNITECH OMEGA API Server...")
    print("Dashboard: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
