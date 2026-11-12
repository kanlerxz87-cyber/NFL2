"""Exact odds conversions and settlement-aware expected value.

American odds must have magnitude >= 100. Probabilities are open interval (0,1).
No sportsbook prices are embedded here.
"""
from __future__ import annotations
import math


def _finite(x: float) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("Expected a finite number")
    return x


def american_to_decimal(odds: float) -> float:
    odds = _finite(odds)
    if abs(odds) < 100:
        raise ValueError("American odds must be <= -100 or >= +100")
    return 1 + (odds / 100 if odds > 0 else 100 / abs(odds))


def decimal_to_american(decimal: float) -> float:
    decimal = _finite(decimal)
    if decimal <= 1:
        raise ValueError("Decimal odds must exceed 1")
    return (decimal - 1) * 100 if decimal >= 2 else -100 / (decimal - 1)


def implied_probability(odds: float) -> float:
    return 1 / american_to_decimal(odds)


def probability_to_american(p: float) -> float:
    p = _finite(p)
    if not 0 < p < 1:
        raise ValueError("Probability must be strictly between 0 and 1")
    return decimal_to_american(1 / p)


def devig_multiplicative(odds: list[float]) -> dict:
    """Proportional normalization; an assumption, not unique 'true' probability."""
    if len(odds) < 2:
        raise ValueError("At least two outcomes are required")
    raw = [implied_probability(o) for o in odds]
    total = sum(raw)
    if total <= 1:
        raise ValueError("A positive overround is required for this de-vig method")
    return {"implied": raw, "fair": [x / total for x in raw],
            "overround": total - 1, "normalized_margin": 1 - 1 / total,
            "method": "multiplicative", "warning": "Actual book hold depends on stake distribution; de-vig method is an assumption."}


def expected_value(p_win: float, decimal: float, p_push: float = 0) -> float:
    p_win, decimal, p_push = map(_finite, (p_win, decimal, p_push))
    if decimal <= 1 or not 0 <= p_win <= 1 or not 0 <= p_push <= 1 or p_win + p_push > 1:
        raise ValueError("Invalid probability or decimal odds")
    return p_win * (decimal - 1) - (1 - p_win - p_push)


def kelly_fraction(p_win: float, decimal: float, p_push: float = 0, fraction: float = 0.25, cap: float = 0.01) -> float:
    """Research calculator only; capped, never negative, no automatic betting."""
    p_win, decimal, p_push, fraction, cap = map(_finite, (p_win, decimal, p_push, fraction, cap))
    if not 0 <= fraction <= 1 or not 0 <= cap <= 1:
        raise ValueError("Kelly fraction and cap must be in [0,1]")
    b = decimal - 1
    if b <= 0:
        raise ValueError("Decimal odds must exceed 1")
    # With pushes, solve p*b*f/(1+b*f) - q/(1-f) = 0.
    full = (b * p_win - (1 - p_win - p_push)) / (b * (p_win + p_push)) if p_win + p_push else 0
    return min(cap, fraction * max(0, full))


def fair_decimal_from_outcomes(p_win: float, p_push: float = 0) -> float:
    p_win, p_push = map(_finite, (p_win, p_push))
    if p_win <= 0 or p_push < 0 or p_win + p_push > 1:
        raise ValueError("Invalid win/push probabilities")
    return (1 - p_push) / p_win


def parlay_decimal(odds: list[float]) -> float:
    """Displayed parlay price only; NOT a joint-probability estimate."""
    if len(odds) < 2:
        raise ValueError("A parlay requires at least two legs")
    result = 1.0
    for o in odds:
        result *= american_to_decimal(o)
    return result
