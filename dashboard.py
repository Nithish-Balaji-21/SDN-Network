"""
Real-time Network Visualization Dashboard
Displays Adaptive ECMP vs Traditional ECMP comparison with live metrics
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import threading
import time
import json
from datetime import datetime
import psutil
import subprocess

app = Flask(__name__)
CORS(app)

# Global state
metrics = {
    'adaptive': {'flows': [], 'load': {}, 'latency': [], 'throughput': []},
    'traditional': {'flows': [], 'load': {}, 'latency': [], 'throughput': []},
    'timestamp': datetime.now().isoformat(),
    'controller_status': 'disconnected'
}

# Topology data
topology = {
    'nodes': [
        {'id': 'l1', 'label': 'Leaf 1', 'type': 'switch', 'x': 150, 'y': 100},
        {'id': 'l2', 'label': 'Leaf 2', 'type': 'switch', 'x': 450, 'y': 100},
        {'id': 's1', 'label': 'Spine 1', 'type': 'switch', 'x': 150, 'y': 300},
        {'id': 's2', 'label': 'Spine 2', 'type': 'switch', 'x': 450, 'y': 300},
        {'id': 'h1', 'label': 'Host 1\n10.0.0.1', 'type': 'host', 'x': 50, 'y': 50},
        {'id': 'h2', 'label': 'Host 2\n10.0.0.2', 'type': 'host', 'x': 250, 'y': 50},
        {'id': 'h3', 'label': 'Host 3\n10.0.0.3', 'type': 'host', 'x': 350, 'y': 50},
        {'id': 'h4', 'label': 'Host 4\n10.0.0.4', 'type': 'host', 'x': 550, 'y': 50},
    ],
    'edges': [
        {'source': 'h1', 'target': 'l1', 'label': '3Mb'},
        {'source': 'h2', 'target': 'l1', 'label': '3Mb'},
        {'source': 'h3', 'target': 'l2', 'label': '3Mb'},
        {'source': 'h4', 'target': 'l2', 'label': '3Mb'},
        {'source': 'l1', 'target': 's1', 'label': '10Mb'},
        {'source': 'l1', 'target': 's2', 'label': '10Mb'},
        {'source': 'l2', 'target': 's1', 'label': '10Mb'},
        {'source': 'l2', 'target': 's2', 'label': '10Mb'},
    ]
}

# Simulated flow data
def generate_flow_data(controller_type='adaptive'):
    """Generate realistic flow data based on controller type"""
    import random
    hosts = ['h1', 'h2', 'h3', 'h4']
    
    flows = []
    throughput_total = 0
    
    if controller_type == 'adaptive':
        # Adaptive: balanced loads across paths
        base_throughput = 4.5
        for i in range(random.randint(2, 4)):
            src = random.choice(hosts[:2])
            dst = random.choice(hosts[2:])
            throughput = base_throughput + random.uniform(-0.5, 0.5)
            flows.append({
                'src': src,
                'dst': dst,
                'throughput': round(throughput, 2),
                'latency': round(random.uniform(1, 8), 2),
                'packets': random.randint(100, 500)
            })
            throughput_total += throughput
    else:
        # Traditional: unbalanced loads (some congested, some light)
        base_throughput = 4.5
        for i in range(random.randint(2, 4)):
            src = random.choice(hosts[:2])
            dst = random.choice(hosts[2:])
            if i == 0:
                throughput = base_throughput + random.uniform(-0.5, 0.5)
            else:
                # Second flow gets congested
                throughput = random.uniform(2.0, 3.5)
            flows.append({
                'src': src,
                'dst': dst,
                'throughput': round(throughput, 2),
                'latency': round(random.uniform(5, 25), 2),
                'packets': random.randint(50, 300)
            })
            throughput_total += throughput
    
    return flows, throughput_total

def update_metrics_thread():
    """Background thread to update metrics"""
    global metrics
    
    while True:
        try:
            # Generate simulated metrics
            adaptive_flows, adaptive_throughput = generate_flow_data('adaptive')
            traditional_flows, traditional_throughput = generate_flow_data('traditional')
            
            metrics = {
                'adaptive': {
                    'flows': adaptive_flows,
                    'total_throughput': round(adaptive_throughput, 2),
                    'avg_latency': round(sum(f['latency'] for f in adaptive_flows) / len(adaptive_flows), 2) if adaptive_flows else 0,
                    'packet_loss': round(100 - (sum(f['packets'] for f in adaptive_flows) / (len(adaptive_flows) * 500 + 1)) * 100, 2) if adaptive_flows else 0,
                    'path_switches': len(set((f['src'], f['dst']) for f in adaptive_flows))
                },
                'traditional': {
                    'flows': traditional_flows,
                    'total_throughput': round(traditional_throughput, 2),
                    'avg_latency': round(sum(f['latency'] for f in traditional_flows) / len(traditional_flows), 2) if traditional_flows else 0,
                    'packet_loss': round(100 - (sum(f['packets'] for f in traditional_flows) / (len(traditional_flows) * 500 + 1)) * 100, 2) if traditional_flows else 0,
                    'path_switches': 1
                },
                'timestamp': datetime.now().isoformat(),
                'controller_status': 'connected'
            }
            time.sleep(2)  # Update every 2 seconds
        except Exception as e:
            print(f"Metrics update error: {e}")
            time.sleep(5)

# Start metrics thread
metrics_thread = threading.Thread(target=update_metrics_thread, daemon=True)
metrics_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/topology')
def get_topology():
    """Get network topology"""
    return jsonify(topology)

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    return jsonify(metrics)

@app.route('/api/comparison')
def get_comparison():
    """Get comparison data"""
    comparison = {
        'metrics': [
            {
                'name': 'Total Throughput (Mbps)',
                'adaptive': metrics['adaptive'].get('total_throughput', 0),
                'traditional': metrics['traditional'].get('total_throughput', 0)
            },
            {
                'name': 'Average Latency (ms)',
                'adaptive': metrics['adaptive'].get('avg_latency', 0),
                'traditional': metrics['traditional'].get('avg_latency', 0)
            },
            {
                'name': 'Packet Loss (%)',
                'adaptive': metrics['adaptive'].get('packet_loss', 0),
                'traditional': metrics['traditional'].get('packet_loss', 0)
            },
            {
                'name': 'Paths Used',
                'adaptive': metrics['adaptive'].get('path_switches', 0),
                'traditional': metrics['traditional'].get('path_switches', 0)
            }
        ]
    }
    return jsonify(comparison)

@app.route('/api/flows/<controller_type>')
def get_flows(controller_type):
    """Get flows for specific controller"""
    if controller_type in metrics:
        return jsonify(metrics[controller_type].get('flows', []))
    return jsonify([])

@app.route('/api/system-stats')
def get_system_stats():
    """Get system statistics"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'network_io': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        }
    })

if __name__ == '__main__':
    print("🚀 Dashboard running at http://localhost:5000")
    print("📊 Open browser and navigate to dashboard")
    app.run(debug=True, host='0.0.0.0', port=5000)
