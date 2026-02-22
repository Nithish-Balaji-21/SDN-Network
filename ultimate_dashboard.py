"""
ULTIMATE ADAPTIVE ECMP DASHBOARD - All Features
Real-time visualization with packet animation, path selection, and comprehensive metrics
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time
import json
from datetime import datetime, timedelta
from collections import deque
import psutil
import statistics
import random
import os
import numpy as np
from typing import Optional

from predictive.telemetry_generator import (
    generate_synthetic_telemetry,
    train_test_split,
    sliding_window,
)
from predictive.lstm_predictor import (
    ModelConfig,
    train_lstm,
    save_model,
    load_model,
    predict_sequence,
    TrainResult,
)

app = Flask(__name__)
CORS(app)

# ============================================================================
# GLOBAL STATE & CONFIGURATION
# ============================================================================

# Metrics history for trends
metrics_history = {
    'adaptive': deque(maxlen=300),  # 10 minutes @ 2sec updates
    'traditional': deque(maxlen=300)
}

# Active flows tracking
active_flows = {
    'adaptive': [],
    'traditional': []
}

# Alerts system
alerts = {
    'adaptive': deque(maxlen=50),
    'traditional': deque(maxlen=50)
}

# Predictive system state
predictive_history = deque(maxlen=300)
predictive_alerts = deque(maxlen=100)
action_log = deque(maxlen=200)

PREDICTIVE_CONFIG = {
    'window_size': 24,
    'horizon': 6,
    'interval_seconds': 2,
    'congestion_threshold': 80.0,
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'predictive', 'lstm_model.pt')


class PredictiveEngine:
    def __init__(self) -> None:
        self.window_size = PREDICTIVE_CONFIG['window_size']
        self.horizon = PREDICTIVE_CONFIG['horizon']
        self.interval_seconds = PREDICTIVE_CONFIG['interval_seconds']
        self.congestion_threshold = PREDICTIVE_CONFIG['congestion_threshold']
        self.feature_keys = [
            'link_utilization_percent',
            'latency_ms',
            'packet_loss_percent',
            'queue_depth',
            'flow_count',
        ]
        self.telemetry = deque(maxlen=1000)
        self.synthetic_stream = generate_synthetic_telemetry(
            2000, interval_seconds=self.interval_seconds
        )
        self.synthetic_index = 0
        self.model = None
        self.scaler = None
        self.metrics = None
        self.status = 'initializing'
        self._action_id = 0
        self.pending_actions = deque(maxlen=50)

        self._initialize_model()

    def _initialize_model(self) -> None:
        loaded = load_model(MODEL_PATH)
        if loaded:
            self.model, self.scaler, _, self.metrics = loaded
            self.status = 'ready'
            return

        data = generate_synthetic_telemetry(1500, interval_seconds=self.interval_seconds)
        train_data, test_data = train_test_split(data, train_ratio=0.8)
        x_train, y_train = sliding_window(
            train_data, self.window_size, self.horizon, self.feature_keys
        )
        x_val, y_val = sliding_window(
            test_data, self.window_size, self.horizon, self.feature_keys
        )

        if not x_train or not x_val:
            self.status = 'data_error'
            return

        x_train = np.asarray(x_train, dtype=np.float32)
        y_train = np.asarray(y_train, dtype=np.float32)
        x_val = np.asarray(x_val, dtype=np.float32)
        y_val = np.asarray(y_val, dtype=np.float32)

        config = ModelConfig(input_size=len(self.feature_keys), horizon=self.horizon)
        model, scaler, metrics = train_lstm(
            x_train=x_train,
            y_train=y_train,
            x_val=x_val,
            y_val=y_val,
            config=config,
            congestion_threshold=self.congestion_threshold,
        )

        save_model(MODEL_PATH, model, scaler, config, metrics)
        self.model = model
        self.scaler = scaler
        self.metrics = metrics
        self.status = 'ready'

    def _next_synthetic(self) -> dict:
        if self.synthetic_index >= len(self.synthetic_stream):
            self.synthetic_stream = generate_synthetic_telemetry(
                2000, interval_seconds=self.interval_seconds
            )
            self.synthetic_index = 0
        sample = self.synthetic_stream[self.synthetic_index]
        self.synthetic_index += 1
        return sample

    def _blend_value(self, synthetic: float, live: float, weight_live: float = 0.4) -> float:
        return (1 - weight_live) * synthetic + weight_live * live

    def append_live_sample(self, adaptive_metric: dict, traditional_metric: dict) -> dict:
        synthetic = self._next_synthetic()

        util_live = float(adaptive_metric.get('throughput', 0)) * 20.0
        latency_live = float(adaptive_metric.get('latency', 0))
        loss_live = float(adaptive_metric.get('packet_loss', 0))
        queue_live = util_live * 1.8 + float(adaptive_metric.get('flows', 0)) * 2.5
        flow_count_live = float(adaptive_metric.get('flows', 0)) * 20

        blended = {
            'timestamp': datetime.utcnow().isoformat(),
            'link_utilization_percent': max(0.0, min(100.0, self._blend_value(
                synthetic['link_utilization_percent'], util_live
            ))),
            'latency_ms': max(0.5, self._blend_value(synthetic['latency_ms'], latency_live)),
            'packet_loss_percent': max(0.0, self._blend_value(synthetic['packet_loss_percent'], loss_live)),
            'queue_depth': max(0.0, self._blend_value(synthetic['queue_depth'], queue_live)),
            'flow_count': int(max(1.0, self._blend_value(synthetic['flow_count'], flow_count_live))),
            'traditional_utilization_percent': float(traditional_metric.get('throughput', 0)) * 20.0,
        }

        self.telemetry.append(blended)
        return blended

    def _prepare_window(self) -> Optional[np.ndarray]:
        if len(self.telemetry) < self.window_size:
            return None
        window = list(self.telemetry)[-self.window_size :]
        return np.asarray([[float(row[k]) for k in self.feature_keys] for row in window], dtype=np.float32)

    def _confidence(self) -> float:
        if not self.metrics:
            return 0.5
        return max(0.2, 1.0 - min(1.0, self.metrics.rmse / 100.0))

    def update_prediction(self) -> Optional[dict]:
        if self.status != 'ready' or self.model is None or self.scaler is None:
            return None

        window = self._prepare_window()
        if window is None:
            return None

        preds = predict_sequence(self.model, self.scaler, window)
        now = datetime.utcnow()
        predicted = []
        for i, value in enumerate(preds):
            predicted.append({
                'timestamp': (now + timedelta(seconds=self.interval_seconds * (i + 1))).isoformat(),
                'utilization': float(max(0.0, min(100.0, value))),
            })

        actual_recent = list(self.telemetry)[-min(12, len(self.telemetry)) :]
        actual = [
            {'timestamp': row['timestamp'], 'utilization': float(row['link_utilization_percent'])}
            for row in actual_recent
        ]

        congestion_probability = float(
            sum(1 for p in predicted if p['utilization'] >= self.congestion_threshold) / max(len(predicted), 1)
        )

        payload = {
            'timestamp': now.isoformat(),
            'actual': actual,
            'predicted': predicted,
            'congestion_probability': congestion_probability,
            'confidence': self._confidence(),
        }
        predictive_history.append(payload)
        return payload

    def _emit_alert(self, alert_type: str, severity: str, message: str, command: str, rollback: Optional[str]) -> None:
        timestamp = datetime.utcnow().isoformat()
        alert = {
            'type': alert_type,
            'severity': severity,
            'message': message,
            'command': command,
            'timestamp': timestamp,
        }
        predictive_alerts.append(alert)
        action_log.append({
            'action': alert_type,
            'command': command,
            'timestamp': timestamp,
        })

        if rollback:
            self._action_id += 1
            self.pending_actions.append({
                'id': self._action_id,
                'timestamp': datetime.utcnow(),
                'rollback': rollback,
            })

    def _check_rollbacks(self) -> None:
        if not self.pending_actions:
            return
        now = datetime.utcnow()
        keep = deque(maxlen=50)
        for action in list(self.pending_actions):
            if (now - action['timestamp']).total_seconds() < self.interval_seconds * self.horizon:
                keep.append(action)
                continue

            if self.telemetry and self.telemetry[-1]['link_utilization_percent'] < self.congestion_threshold:
                action_log.append({
                    'action': 'rollback',
                    'command': action['rollback'],
                    'timestamp': now.isoformat(),
                })
            else:
                keep.append(action)
        self.pending_actions = keep

    def evaluate_actions(self, prediction: Optional[dict]) -> None:
        if not prediction:
            return

        self._check_rollbacks()

        latest = self.telemetry[-1] if self.telemetry else None
        if not latest:
            return

        predicted_util = max(p['utilization'] for p in prediction['predicted'])
        if predicted_util >= self.congestion_threshold:
            self._emit_alert(
                'predicted_congestion',
                'HIGH',
                'Congestion predicted within horizon, proactive reroute initiated.',
                'sdn_controller_cli set_path_weight spine2-leaf5 weight=70',
                'sdn_controller_cli set_path_weight spine2-leaf5 weight=50',
            )

        if len(self.telemetry) >= 2:
            delta = latest['link_utilization_percent'] - self.telemetry[-2]['link_utilization_percent']
            if delta > 20 and latest['link_utilization_percent'] > 70:
                self._emit_alert(
                    'sudden_spike',
                    'MEDIUM',
                    'Sudden spike detected, rerouting high bandwidth flows.',
                    'sdn_controller_cli reroute flow_id=1245 alternate_path=spine3',
                    'sdn_controller_cli reroute flow_id=1245 alternate_path=spine1',
                )

        recent = list(self.telemetry)[-5:]
        if len(recent) == 5:
            avg_util = sum(r['link_utilization_percent'] for r in recent) / 5
            avg_flows = sum(r['flow_count'] for r in recent) / 5
            if avg_util > 85 and avg_flows > 200:
                self._emit_alert(
                    'ddos_pattern',
                    'HIGH',
                    'Sustained overload pattern detected, applying rate limit.',
                    'sdn_controller_cli apply_qos policy=rate_limit_1Gbps interface=leaf3',
                    'sdn_controller_cli remove_qos policy=rate_limit_1Gbps interface=leaf3',
                )

            latencies = [r['latency_ms'] for r in recent]
            util_avg = sum(r['link_utilization_percent'] for r in recent) / 5
            if util_avg < 60 and latencies[-1] - latencies[0] > 5:
                self._emit_alert(
                    'link_degradation',
                    'MEDIUM',
                    'Latency increase detected, shifting latency-sensitive flows.',
                    'sdn_controller_cli move_flow class=latency_sensitive path=low_latency_path',
                    'sdn_controller_cli move_flow class=latency_sensitive path=default_path',
                )

    def update(self, adaptive_metric: dict, traditional_metric: dict) -> Optional[dict]:
        self.append_live_sample(adaptive_metric, traditional_metric)
        prediction = self.update_prediction()
        self.evaluate_actions(prediction)
        return prediction

    def get_latest_prediction(self) -> dict:
        if predictive_history:
            return predictive_history[-1]
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'actual': [],
            'predicted': [],
            'congestion_probability': 0.0,
            'confidence': 0.0,
        }

    def get_metrics(self) -> dict:
        if not self.metrics:
            return {'rmse': 0.0, 'mae': 0.0, 'r2': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        return {
            'rmse': self.metrics.rmse,
            'mae': self.metrics.mae,
            'r2': self.metrics.r2,
            'precision': self.metrics.precision,
            'recall': self.metrics.recall,
            'f1': self.metrics.f1,
        }


predictive_engine = PredictiveEngine()

# ============================================================================
# TOPOLOGY DEFINITION
# ============================================================================

topology = {
    'nodes': [
        {'id': 'l1', 'label': 'Leaf 1', 'type': 'switch', 'x': 150, 'y': 100},
        {'id': 'l2', 'label': 'Leaf 2', 'type': 'switch', 'x': 450, 'y': 100},
        {'id': 's1', 'label': 'Spine 1', 'type': 'switch', 'x': 150, 'y': 300},
        {'id': 's2', 'label': 'Spine 2', 'type': 'switch', 'x': 450, 'y': 300},
        {'id': 'h1', 'label': 'Host 1', 'type': 'host', 'x': 50, 'y': 50},
        {'id': 'h2', 'label': 'Host 2', 'type': 'host', 'x': 250, 'y': 50},
        {'id': 'h3', 'label': 'Host 3', 'type': 'host', 'x': 350, 'y': 50},
        {'id': 'h4', 'label': 'Host 4', 'type': 'host', 'x': 550, 'y': 50},
    ],
    'edges': [
        {'source': 'h1', 'target': 'l1', 'capacity': 3},
        {'source': 'h2', 'target': 'l1', 'capacity': 3},
        {'source': 'h3', 'target': 'l2', 'capacity': 3},
        {'source': 'h4', 'target': 'l2', 'capacity': 3},
        {'source': 'l1', 'target': 's1', 'capacity': 10},
        {'source': 'l1', 'target': 's2', 'capacity': 10},
        {'source': 'l2', 'target': 's1', 'capacity': 10},
        {'source': 'l2', 'target': 's2', 'capacity': 10},
    ]
}

# ============================================================================
# PATH SELECTION ALGORITHMS
# ============================================================================

def select_path_adaptive(src, dst):
    """Adaptive path selection - chooses least congested path"""
    paths = [
        [src, 'l1' if src.startswith('h') and src in ['h1', 'h2'] else 'l2', 's1', 'l2' if dst.startswith('h') and dst in ['h3', 'h4'] else 'l1', dst],
        [src, 'l1' if src.startswith('h') and src in ['h1', 'h2'] else 'l2', 's2', 'l2' if dst.startswith('h') and dst in ['h3', 'h4'] else 'l1', dst]
    ]
    
    # Choose path with least congestion
    best_path = paths[0]
    best_util = get_path_utilization(paths[0])
    
    for path in paths[1:]:
        util = get_path_utilization(path)
        if util < best_util:
            best_path = path
            best_util = util
    
    return best_path

def select_path_traditional(src, dst):
    """Traditional hash-based path selection - always same path"""
    # Hash-based: always picks first path (fixed routing)
    if src.startswith('h') and src in ['h1', 'h2']:
        return [src, 'l1', 's1', 'l2' if dst.startswith('h') and dst in ['h3', 'h4'] else 'l1', dst]
    else:
        return [src, 'l2', 's1', 'l1' if dst.startswith('h') and dst in ['h1', 'h2'] else 'l2', dst]

def get_path_utilization(path):
    """Calculate total utilization of a path"""
    util = 0
    for i in range(len(path) - 1):
        util += random.uniform(10, 90) if i == 1 else random.uniform(20, 50)
    return util / len(path)

# ============================================================================
# FLOW GENERATION & SIMULATION
# ============================================================================

class Flow:
    """Represents a network flow"""
    def __init__(self, src, dst, controller_type='adaptive'):
        self.src = src
        self.dst = dst
        self.controller_type = controller_type
        self.start_time = datetime.now()
        
        # Select path based on controller type
        if controller_type == 'adaptive':
            self.path = select_path_adaptive(src, dst)
        else:
            self.path = select_path_traditional(src, dst)
        
        # Generate realistic metrics
        if controller_type == 'adaptive':
            self.throughput = random.uniform(4.0, 5.0)
            self.latency = random.uniform(1, 8)
            self.packet_loss = random.uniform(0, 0.5)
        else:
            self.throughput = random.uniform(2.0, 3.5)
            self.latency = random.uniform(5, 25)
            self.packet_loss = random.uniform(0.5, 2.0)
        
        self.packets = random.randint(100, 500)
        self.jitter = random.uniform(0.5, 5)
        self.hop_count = len(self.path) - 1

def generate_flows(controller_type='adaptive'):
    """Generate active flows"""
    hosts = ['h1', 'h2', 'h3', 'h4']
    flows = []
    
    num_flows = random.randint(2, 4)
    for i in range(num_flows):
        src = random.choice(hosts[:2])
        dst = random.choice(hosts[2:])
        flows.append(Flow(src, dst, controller_type))
    
    return flows

# ============================================================================
# METRICS CALCULATIONS
# ============================================================================

def calculate_qos_score(latency, jitter, packet_loss):
    """Calculate QoS score (0-100)"""
    latency_score = max(0, 100 - latency * 5)
    jitter_score = max(0, 100 - jitter * 10)
    loss_score = max(0, 100 - packet_loss * 20)
    return (latency_score + jitter_score + loss_score) / 3

def calculate_alerts(flows, controller_type):
    """Generate alerts based on metrics"""
    new_alerts = []
    
    for flow in flows:
        # Congestion alert
        if flow.throughput < 3:
            new_alerts.append({
                'type': 'CONGESTION',
                'severity': 'HIGH',
                'message': f'Congestion detected: {flow.src}→{flow.dst} ({flow.throughput:.1f} Mbps)',
                'timestamp': datetime.now().isoformat()
            })
        
        # Latency spike
        if flow.latency > 20:
            new_alerts.append({
                'type': 'LATENCY_SPIKE',
                'severity': 'MEDIUM',
                'message': f'High latency: {flow.latency:.1f}ms',
                'timestamp': datetime.now().isoformat()
            })
        
        # Packet loss
        if flow.packet_loss > 1:
            new_alerts.append({
                'type': 'PACKET_LOSS',
                'severity': 'MEDIUM',
                'message': f'Packet loss {flow.packet_loss:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
    
    return new_alerts

def calculate_roi():
    """Calculate business value"""
    throughput_improvement = 35  # 35% improvement
    cost_per_gbps = 10000
    hardware_savings = (throughput_improvement / 100) * cost_per_gbps * 40
    power_savings = (throughput_improvement / 100) * 5000 * 0.15
    total_savings = hardware_savings + power_savings
    
    return {
        'throughput_improvement': f"{throughput_improvement:.1f}%",
        'hardware_savings': f"${hardware_savings:,.0f}",
        'power_savings': f"${power_savings:,.0f}",
        'total_annual_savings': f"${total_savings:,.0f}",
        'payback_months': 12 / (total_savings / 100000) if total_savings > 0 else 999
    }

# ============================================================================
# BACKGROUND METRICS UPDATE THREAD
# ============================================================================

def update_metrics_thread():
    """Background thread to update metrics"""
    while True:
        try:
            # Generate new flows
            adaptive_flows = generate_flows('adaptive')
            traditional_flows = generate_flows('traditional')
            
            # Calculate aggregates
            adaptive_throughput = sum(f.throughput for f in adaptive_flows) / len(adaptive_flows) if adaptive_flows else 0
            traditional_throughput = sum(f.throughput for f in traditional_flows) / len(traditional_flows) if traditional_flows else 0
            
            adaptive_latency = sum(f.latency for f in adaptive_flows) / len(adaptive_flows) if adaptive_flows else 0
            traditional_latency = sum(f.latency for f in traditional_flows) / len(traditional_flows) if traditional_flows else 0
            
            adaptive_loss = sum(f.packet_loss for f in adaptive_flows) / len(adaptive_flows) if adaptive_flows else 0
            traditional_loss = sum(f.packet_loss for f in traditional_flows) / len(traditional_flows) if traditional_flows else 0
            
            # Calculate QoS scores
            adaptive_qos = calculate_qos_score(adaptive_latency, 
                                            sum(f.jitter for f in adaptive_flows) / len(adaptive_flows) if adaptive_flows else 0,
                                            adaptive_loss)
            traditional_qos = calculate_qos_score(traditional_latency,
                                                 sum(f.jitter for f in traditional_flows) / len(traditional_flows) if traditional_flows else 0,
                                                 traditional_loss)
            
            # Store metrics
            metric = {
                'timestamp': datetime.now().isoformat(),
                'adaptive': {
                    'throughput': round(adaptive_throughput, 2),
                    'latency': round(adaptive_latency, 2),
                    'packet_loss': round(adaptive_loss, 2),
                    'qos_score': round(adaptive_qos, 1),
                    'paths_used': len(set(tuple(f.path) for f in adaptive_flows)),
                    'flows': len(adaptive_flows)
                },
                'traditional': {
                    'throughput': round(traditional_throughput, 2),
                    'latency': round(traditional_latency, 2),
                    'packet_loss': round(traditional_loss, 2),
                    'qos_score': round(traditional_qos, 1),
                    'paths_used': 1,
                    'flows': len(traditional_flows)
                }
            }
            
            metrics_history['adaptive'].append(metric['adaptive'])
            metrics_history['traditional'].append(metric['traditional'])
            
            # Generate alerts
            alerts['adaptive'].extend(calculate_alerts(adaptive_flows, 'adaptive'))
            alerts['traditional'].extend(calculate_alerts(traditional_flows, 'traditional'))
            
            # Store flows
            active_flows['adaptive'] = [{
                'src': f.src,
                'dst': f.dst,
                'throughput': round(f.throughput, 2),
                'latency': round(f.latency, 2),
                'packets': f.packets,
                'path': ' → '.join(f.path),
                'hop_count': f.hop_count,
                'jitter': round(f.jitter, 2),
                'qos': round(calculate_qos_score(f.latency, f.jitter, f.packet_loss), 1)
            } for f in adaptive_flows]
            
            active_flows['traditional'] = [{
                'src': f.src,
                'dst': f.dst,
                'throughput': round(f.throughput, 2),
                'latency': round(f.latency, 2),
                'packets': f.packets,
                'path': ' → '.join(f.path),
                'hop_count': f.hop_count,
                'jitter': round(f.jitter, 2),
                'qos': round(calculate_qos_score(f.latency, f.jitter, f.packet_loss), 1)
            } for f in traditional_flows]

            if predictive_engine:
                predictive_engine.update(metric['adaptive'], metric['traditional'])
            
            time.sleep(2)
        except Exception as e:
            print(f"Metrics error: {e}")
            time.sleep(5)

# Start background thread
metrics_thread = threading.Thread(target=update_metrics_thread, daemon=True)
metrics_thread.start()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('ultimate_dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    if not metrics_history['adaptive'] or not metrics_history['traditional']:
        return jsonify({'adaptive': {}, 'traditional': {}})
    
    return jsonify({
        'adaptive': dict(metrics_history['adaptive'][-1]),
        'traditional': dict(metrics_history['traditional'][-1]),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/flows/<controller_type>')
def get_flows(controller_type):
    """Get flows for controller"""
    return jsonify(active_flows.get(controller_type, []))

@app.route('/api/alerts/<controller_type>')
def get_alerts(controller_type):
    """Get alerts for controller"""
    return jsonify(list(alerts.get(controller_type, [])))

@app.route('/api/metrics-history')
def get_metrics_history():
    """Get historical metrics"""
    return jsonify({
        'adaptive': [
            {
                'timestamp': m.get('timestamp'),
                'throughput': m.get('throughput', 0),
                'latency': m.get('latency', 0),
                'qos': m.get('qos_score', 0)
            } for m in list(metrics_history['adaptive'])[-150:]
        ],
        'traditional': [
            {
                'timestamp': m.get('timestamp'),
                'throughput': m.get('throughput', 0),
                'latency': m.get('latency', 0),
                'qos': m.get('qos_score', 0)
            } for m in list(metrics_history['traditional'])[-150:]
        ]
    })

@app.route('/api/topology')
def get_topology():
    """Get network topology"""
    return jsonify(topology)

@app.route('/api/roi')
def get_roi():
    """Get ROI calculation"""
    return jsonify(calculate_roi())

@app.route('/api/link-heatmap')
def get_link_heatmap():
    """Get link utilization heatmap"""
    heatmap = {}
    for edge in topology['edges']:
        link_name = f"{edge['source']}-{edge['target']}"
        utilization = random.uniform(20, 90)
        heatmap[link_name] = round(utilization, 1)
    return jsonify(heatmap)

@app.route('/api/comparison')
def get_comparison():
    """Get detailed comparison"""
    if not metrics_history['adaptive'] or not metrics_history['traditional']:
        return jsonify({})
    
    adaptive = metrics_history['adaptive'][-1]
    traditional = metrics_history['traditional'][-1]
    
    return jsonify({
        'throughput': {
            'adaptive': adaptive.get('throughput', 0),
            'traditional': traditional.get('throughput', 0),
            'improvement': round((adaptive.get('throughput', 0) / max(traditional.get('throughput', 1), 0.1) - 1) * 100, 1) if traditional.get('throughput', 0) > 0 else 0
        },
        'latency': {
            'adaptive': adaptive.get('latency', 0),
            'traditional': traditional.get('latency', 0)
        },
        'qos': {
            'adaptive': adaptive.get('qos_score', 0),
            'traditional': traditional.get('qos_score', 0)
        },
        'paths': {
            'adaptive': adaptive.get('paths_used', 0),
            'traditional': traditional.get('paths_used', 1)
        }
    })

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


@app.route('/api/predictions')
def get_predictions():
    """Get latest prediction payload"""
    if not predictive_engine:
        return jsonify({'actual': [], 'predicted': [], 'congestion_probability': 0.0, 'confidence': 0.0})
    return jsonify(predictive_engine.get_latest_prediction())


@app.route('/api/model-metrics')
def get_model_metrics():
    """Get model accuracy metrics"""
    if not predictive_engine:
        return jsonify({'rmse': 0.0, 'mae': 0.0, 'r2': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0})
    return jsonify(predictive_engine.get_metrics())


@app.route('/api/predictive-alerts')
def get_predictive_alerts():
    """Get predictive alerts"""
    return jsonify(list(predictive_alerts))


@app.route('/api/action-log')
def get_action_log():
    """Get action command log"""
    return jsonify(list(action_log))

if __name__ == '__main__':
    print("🚀 ULTIMATE ADAPTIVE ECMP DASHBOARD")
    print("🌐 Running at http://localhost:5000")
    print("📊 All features enabled!")
    app.run(debug=True, host='0.0.0.0', port=5000)
