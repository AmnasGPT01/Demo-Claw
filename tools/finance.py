"""Finance tools for the agent factory.

Each tool is a pure function that takes simple Python types and returns a dict.
The factory's builder wires these by name into the agent's tool set.

Conventions:
- Prices are dicts: {date: price} with ISO date strings.
- Returns are dicts: {date: return} where return = (p_t / p_{t-1}) - 1.
- All ratios are annualized by default unless noted.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Callable


# --- Data source -----------------------------------------------------------

def get_prices(ticker: str, start: str, end: str) -> dict:
    """Return a deterministic synthetic price series for the ticker.

    Real implementations would call Yahoo/Alpha Vantage/etc. We use a
    deterministic generator so the demo is reproducible without API keys.
    """
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    if end_d <= start_d:
        raise ValueError("end must be after start")

    # Seed from ticker so different tickers get different (but stable) series.
    seed = sum(ord(c) for c in ticker) % 100
    base = 50.0 + seed
    drift = 0.0004 + (seed % 7) * 0.0001   # small positive drift
    vol = 0.015 + (seed % 5) * 0.002        # daily volatility

    prices: dict[str, float] = {}
    d = start_d
    # Simple deterministic pseudo-random walk: a sine-modulated step.
    step = 0
    while d <= end_d:
        if d.weekday() < 5:  # weekdays only
            shock = math.sin(step * 0.37 + seed) * vol
            base *= 1.0 + drift + shock
            prices[d.isoformat()] = round(base, 4)
            step += 1
        d += timedelta(days=1)
    return prices


# --- Math -------------------------------------------------------------------

def compute_returns(prices: dict) -> dict:
    """Daily simple returns from a price series."""
    if len(prices) < 2:
        raise ValueError("need at least 2 prices")
    sorted_dates = sorted(prices)
    rets = {}
    prev = prices[sorted_dates[0]]
    for d in sorted_dates[1:]:
        p = prices[d]
        rets[d] = (p / prev) - 1.0
        prev = p
    return {d: round(r, 6) for d, r in rets.items()}


def volatility(returns: dict, annualized: bool = True) -> float:
    """Standard deviation of returns. Annualized = x * sqrt(252)."""
    if not returns:
        raise ValueError("no returns")
    n = len(returns)
    mean = sum(returns.values()) / n
    var = sum((r - mean) ** 2 for r in returns.values()) / (n - 1)
    sd = math.sqrt(var)
    return round(sd * math.sqrt(252), 4) if annualized else round(sd, 6)


def sharpe_ratio(returns: dict, risk_free: float = 0.0, annualized: bool = True) -> float:
    """Sharpe = (mean_excess_return / sd) * sqrt(252) by default.

    risk_free is the *daily* risk-free rate (e.g. 0.0001 ~ 2.5% annual).
    """
    if not returns:
        raise ValueError("no returns")
    n = len(returns)
    mean = sum(returns.values()) / n
    excess = mean - risk_free
    sd = volatility(returns, annualized=False)
    if sd == 0:
        return 0.0
    out = excess / sd
    if annualized:
        out *= math.sqrt(252)
    return round(out, 4)


def max_drawdown(prices: dict) -> dict:
    """Largest peak-to-trough decline. Returns {drawdown, peak_date, trough_date}."""
    if not prices:
        raise ValueError("no prices")
    sorted_dates = sorted(prices)
    peak = prices[sorted_dates[0]]
    peak_date = sorted_dates[0]
    max_dd = 0.0
    dd_peak = peak_date
    dd_trough = sorted_dates[0]
    running_peak = peak
    running_peak_date = peak_date
    for d in sorted_dates:
        p = prices[d]
        if p > running_peak:
            running_peak = p
            running_peak_date = d
        dd = (p / running_peak) - 1.0
        if dd < max_dd:
            max_dd = dd
            dd_peak = running_peak_date
            dd_trough = d
    return {
        "drawdown": round(max_dd, 4),
        "peak_date": dd_peak,
        "trough_date": dd_trough,
    }


# --- Registry ---------------------------------------------------------------

# Maps tool name -> callable. The factory builder resolves spec tools from this.
TOOL_REGISTRY: dict[str, Callable] = {
    "get_prices": get_prices,
    "compute_returns": compute_returns,
    "volatility": volatility,
    "sharpe_ratio": sharpe_ratio,
    "max_drawdown": max_drawdown,
}
