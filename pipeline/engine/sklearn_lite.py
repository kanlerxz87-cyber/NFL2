"""Tiny metric helpers (no sklearn dependency in this sandbox)."""
from __future__ import annotations

import numpy as np


def brier(y, p) -> float:
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    return float(np.mean((p - y) ** 2))


def logloss(y, p, eps: float = 1e-12) -> float:
    y = np.asarray(y, float)
    p = np.clip(np.asarray(p, float), eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def wilson_interval(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    w = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (float((c - w) / d), float((c + w) / d))
