"""
PyTorch LSTM predictor for multivariate telemetry forecasting.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


@dataclass
class ModelConfig:
    input_size: int = 5
    hidden_size: int = 64
    num_layers: int = 2
    dropout: float = 0.2
    horizon: int = 6


class MinMaxScaler:
    def __init__(self) -> None:
        self.min = None
        self.max = None

    def fit(self, data: np.ndarray) -> None:
        self.min = data.min(axis=(0, 1), keepdims=True)
        self.max = data.max(axis=(0, 1), keepdims=True)

    def transform(self, data: np.ndarray) -> np.ndarray:
        if self.min is None or self.max is None:
            return data
        denom = np.where((self.max - self.min) == 0, 1.0, (self.max - self.min))
        return (data - self.min) / denom

    def inverse_transform(self, data: np.ndarray, feature_index: int = 0) -> np.ndarray:
        if self.min is None or self.max is None:
            return data
        denom = np.where((self.max - self.min) == 0, 1.0, (self.max - self.min))
        return data * denom[..., feature_index] + self.min[..., feature_index]

    def to_dict(self) -> dict:
        return {
            "min": None if self.min is None else self.min.tolist(),
            "max": None if self.max is None else self.max.tolist(),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "MinMaxScaler":
        scaler = cls()
        if payload.get("min") is not None:
            scaler.min = np.array(payload["min"], dtype=np.float32)
        if payload.get("max") is not None:
            scaler.max = np.array(payload["max"], dtype=np.float32)
        return scaler


class LSTMForecaster(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=config.input_size,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            dropout=config.dropout,
            batch_first=True,
        )
        self.head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(config.hidden_size // 2, config.horizon),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(x)
        last_step = output[:, -1, :]
        return self.head(last_step)


@dataclass
class TrainResult:
    rmse: float
    mae: float
    r2: float
    precision: float
    recall: float
    f1: float


class EarlyStopper:
    def __init__(self, patience: int = 8, min_delta: float = 1e-4) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.best = math.inf
        self.counter = 0

    def should_stop(self, value: float) -> bool:
        if value < self.best - self.min_delta:
            self.best = value
            self.counter = 0
            return False
        self.counter += 1
        return self.counter >= self.patience


def _metrics_regression(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float, float]:
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = math.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return rmse, mae, r2


def _metrics_classification(y_true: np.ndarray, y_pred: np.ndarray, threshold: float) -> tuple[float, float, float]:
    true_pos = np.sum((y_true >= threshold) & (y_pred >= threshold))
    false_pos = np.sum((y_true < threshold) & (y_pred >= threshold))
    false_neg = np.sum((y_true >= threshold) & (y_pred < threshold))

    precision = true_pos / max(true_pos + false_pos, 1)
    recall = true_pos / max(true_pos + false_neg, 1)
    f1 = (2 * precision * recall / max(precision + recall, 1e-8))
    return precision, recall, f1


def train_lstm(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    config: ModelConfig,
    device: str = "cpu",
    epochs: int = 40,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    congestion_threshold: float = 80.0,
) -> tuple[LSTMForecaster, MinMaxScaler, TrainResult]:
    scaler = MinMaxScaler()
    scaler.fit(x_train)

    x_train_scaled = scaler.transform(x_train)
    x_val_scaled = scaler.transform(x_val)

    model = LSTMForecaster(config).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    stopper = EarlyStopper()

    train_dataset = torch.utils.data.TensorDataset(
        torch.tensor(x_train_scaled, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    x_val_tensor = torch.tensor(x_val_scaled, dtype=torch.float32, device=device)
    y_val_tensor = torch.tensor(y_val, dtype=torch.float32, device=device)

    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            val_preds = model(x_val_tensor)
            val_loss = criterion(val_preds, y_val_tensor).item()

        if stopper.should_stop(val_loss):
            break

    model.eval()
    with torch.no_grad():
        val_preds = model(x_val_tensor).cpu().numpy()

    rmse, mae, r2 = _metrics_regression(y_val, val_preds)
    precision, recall, f1 = _metrics_classification(y_val, val_preds, congestion_threshold)

    result = TrainResult(
        rmse=float(rmse),
        mae=float(mae),
        r2=float(r2),
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
    )

    return model, scaler, result


def save_model(path: str, model: LSTMForecaster, scaler: MinMaxScaler, config: ModelConfig, metrics: TrainResult) -> None:
    payload = {
        "model_state": model.state_dict(),
        "config": config.__dict__,
        "scaler": scaler.to_dict(),
        "metrics": metrics.__dict__,
    }
    torch.save(payload, path)


def load_model(path: str, device: str = "cpu") -> Optional[Tuple[LSTMForecaster, MinMaxScaler, ModelConfig, TrainResult]]:
    if not os.path.exists(path):
        return None
    payload: dict[str, Any] = torch.load(path, map_location=device)

    config = ModelConfig(**payload.get("config", {}))
    model = LSTMForecaster(config).to(device)
    model.load_state_dict(payload["model_state"])
    model.eval()

    scaler = MinMaxScaler.from_dict(payload.get("scaler", {}))
    metrics = TrainResult(**payload.get("metrics", {}))
    return model, scaler, config, metrics


def predict_sequence(
    model: LSTMForecaster,
    scaler: MinMaxScaler,
    window: np.ndarray,
    device: str = "cpu",
) -> np.ndarray:
    if window.ndim == 2:
        window = window[None, :, :]
    window_scaled = scaler.transform(window)
    tensor = torch.tensor(window_scaled, dtype=torch.float32, device=device)
    with torch.no_grad():
        preds = model(tensor).cpu().numpy()[0]
    return preds
