"""
Synthetic telemetry generator for adaptive ECMP prediction.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Optional

FEATURES = [
    "timestamp",
    "link_utilization_percent",
    "latency_ms",
    "packet_loss_percent",
    "queue_depth",
    "flow_count",
]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _noise(scale: float) -> float:
    return random.uniform(-scale, scale)


def _scenario_normal(t: int) -> dict:
    util = 35 + 5 * math.sin(t / 18) + _noise(2)
    latency = 6 + 1.2 * math.sin(t / 14) + _noise(0.5)
    loss = 0.4 + _noise(0.1)
    queue = 20 + 4 * math.sin(t / 22) + _noise(2)
    flows = 80 + 10 * math.sin(t / 20) + _noise(3)
    return {
        "link_utilization_percent": _clamp(util, 10, 60),
        "latency_ms": _clamp(latency, 2, 15),
        "packet_loss_percent": _clamp(loss, 0.0, 1.2),
        "queue_depth": _clamp(queue, 5, 60),
        "flow_count": int(_clamp(flows, 40, 140)),
    }


def _scenario_growth(t: int) -> dict:
    util = 30 + (t / 6) + 8 * math.sin(t / 16) + _noise(3)
    latency = 7 + (t / 40) + _noise(0.8)
    loss = 0.6 + (t / 80) + _noise(0.15)
    queue = 18 + (t / 3) + _noise(3)
    flows = 70 + (t / 3) + _noise(4)
    return {
        "link_utilization_percent": _clamp(util, 25, 95),
        "latency_ms": _clamp(latency, 3, 40),
        "packet_loss_percent": _clamp(loss, 0.1, 2.5),
        "queue_depth": _clamp(queue, 10, 120),
        "flow_count": int(_clamp(flows, 60, 220)),
    }


def _scenario_microburst(t: int) -> dict:
    burst = 50 if t % 18 < 3 else 0
    util = 35 + burst + _noise(5)
    latency = 8 + (burst * 0.15) + _noise(1.2)
    loss = 0.8 + (burst * 0.02) + _noise(0.2)
    queue = 25 + (burst * 0.5) + _noise(4)
    flows = 85 + (burst * 0.3) + _noise(5)
    return {
        "link_utilization_percent": _clamp(util, 20, 100),
        "latency_ms": _clamp(latency, 4, 60),
        "packet_loss_percent": _clamp(loss, 0.1, 4.0),
        "queue_depth": _clamp(queue, 10, 200),
        "flow_count": int(_clamp(flows, 70, 280)),
    }


def _scenario_ddos(t: int) -> dict:
    util = 85 + 8 * math.sin(t / 8) + _noise(4)
    latency = 25 + 5 * math.sin(t / 10) + _noise(2.0)
    loss = 2.5 + _noise(0.4)
    queue = 140 + 20 * math.sin(t / 12) + _noise(8)
    flows = 260 + 30 * math.sin(t / 9) + _noise(10)
    return {
        "link_utilization_percent": _clamp(util, 70, 100),
        "latency_ms": _clamp(latency, 10, 120),
        "packet_loss_percent": _clamp(loss, 1.0, 8.0),
        "queue_depth": _clamp(queue, 80, 280),
        "flow_count": int(_clamp(flows, 180, 420)),
    }


def _scenario_degradation(t: int) -> dict:
    util = 40 + 6 * math.sin(t / 20) + _noise(2.5)
    latency = 18 + 6 * math.sin(t / 16) + _noise(1.5)
    loss = 0.8 + _noise(0.2)
    queue = 30 + 6 * math.sin(t / 18) + _noise(3)
    flows = 90 + 10 * math.sin(t / 19) + _noise(4)
    return {
        "link_utilization_percent": _clamp(util, 25, 70),
        "latency_ms": _clamp(latency, 10, 50),
        "packet_loss_percent": _clamp(loss, 0.2, 2.0),
        "queue_depth": _clamp(queue, 12, 90),
        "flow_count": int(_clamp(flows, 60, 160)),
    }


SCENARIO_MAP = {
    "normal": _scenario_normal,
    "growth": _scenario_growth,
    "microburst": _scenario_microburst,
    "ddos": _scenario_ddos,
    "degradation": _scenario_degradation,
}


def generate_synthetic_telemetry(
    points: int,
    start_time: Optional[datetime] = None,
    interval_seconds: int = 2,
    scenario_schedule: Optional[list[tuple[str, int]]] = None,
) -> list[dict]:
    """
    Generate synthetic telemetry with scenario scheduling.

    scenario_schedule: list of (scenario_name, duration_points)
    """
    if start_time is None:
        start_time = datetime.utcnow()

    if scenario_schedule is None:
        scenario_schedule = [
            ("normal", max(1, points // 5)),
            ("growth", max(1, points // 5)),
            ("microburst", max(1, points // 5)),
            ("ddos", max(1, points // 5)),
            ("degradation", points - 4 * max(1, points // 5)),
        ]

    data = []
    t = 0
    current_time = start_time

    for scenario_name, duration in scenario_schedule:
        generator = SCENARIO_MAP.get(scenario_name, _scenario_normal)
        for _ in range(duration):
            metrics = generator(t)
            metrics["timestamp"] = current_time.isoformat()
            data.append(metrics)
            t += 1
            current_time += timedelta(seconds=interval_seconds)
            if len(data) >= points:
                return data

    return data


def train_test_split(data: list[dict], train_ratio: float = 0.8) -> tuple[list[dict], list[dict]]:
    if not data:
        return [], []
    split_idx = max(1, int(len(data) * train_ratio))
    return data[:split_idx], data[split_idx:]


def sliding_window(
    data: list[dict],
    window_size: int,
    horizon: int,
    feature_keys: Optional[list[str]] = None,
    target_key: str = "link_utilization_percent",
) -> tuple[list[list[list[float]]], list[list[float]]]:
    """
    Prepare sliding windows for sequence-to-sequence prediction.
    Returns X (samples, window, features) and y (samples, horizon).
    """
    if feature_keys is None:
        feature_keys = [
            "link_utilization_percent",
            "latency_ms",
            "packet_loss_percent",
            "queue_depth",
            "flow_count",
        ]

    x_samples = []
    y_samples = []
    total = len(data)

    for i in range(total - window_size - horizon + 1):
        window = data[i : i + window_size]
        target = data[i + window_size : i + window_size + horizon]
        x_samples.append([[float(w[k]) for k in feature_keys] for w in window])
        y_samples.append([float(t[target_key]) for t in target])

    return x_samples, y_samples
