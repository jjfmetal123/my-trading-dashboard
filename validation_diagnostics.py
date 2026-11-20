"""Pure helpers for dashboard signal-validation diagnostics.

These helpers intentionally mirror the cloud worker's score buckets and
symbol/setup de-overlap rule. They do not make trading decisions.
"""
from datetime import date, datetime, timedelta
import math


def score_bucket(score):
    """Return the worker-aligned score bucket, or None for invalid input."""
    try:
        value = float(score)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(value):
        return None
    value = min(100.0, max(0.0, value))
    lower = min(90, int(value // 10) * 10)
    if lower < 50:
        return "00-49"
    if lower == 90:
        return "90-100"
    return f"{lower:02d}-{lower + 9:02d}"


def _parse_signal_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.date()
    except (TypeError, ValueError, OverflowError):
        return None


def _business_days_between_exclusive_start(start, end):
    """Count weekdays in (start, end], matching bdate_range(start, end) - 1."""
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


def deoverlap_events(events, cooldown_sessions=20):
    """Keep first event per symbol/setup until cooldown weekdays have elapsed."""
    if isinstance(cooldown_sessions, bool) or not isinstance(cooldown_sessions, int) or cooldown_sessions < 0:
        raise ValueError("cooldown_sessions must be a non-negative integer")
    ordered = sorted(
        events or [],
        key=lambda event: (
            str(event.get("symbol") or ""),
            str(event.get("setup_type") or ""),
            str(event.get("signal_date") or ""),
        ),
    )
    kept = []
    last_date = {}
    for event in ordered:
        signal_date = _parse_signal_date(event.get("signal_date"))
        if signal_date is None:
            continue
        key = (
            str(event.get("symbol") or "").upper(),
            str(event.get("setup_type") or "").upper(),
        )
        prior = last_date.get(key)
        if prior is not None and _business_days_between_exclusive_start(prior, signal_date) < cooldown_sessions:
            continue
        kept.append(event)
        last_date[key] = signal_date
    return kept


def build_edge_diagnostics(
    events,
    *,
    horizons=("1d", "5d", "10d", "20d"),
    min_return_samples=30,
    min_benchmark_samples=20,
    cost_scenarios_bps=(10, 20, 40, 60),
):
    """Aggregate de-overlapped close-to-close outcomes by setup/score/regime.

    Costs are explicit round-trip assumptions, not measured fills. Returned
    evidence labels are descriptive and never grant trading authority.
    """
    for name, value in (
        ("min_return_samples", min_return_samples),
        ("min_benchmark_samples", min_benchmark_samples),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if not horizons or len(set(horizons)) != len(horizons) or any(
        not isinstance(h, str) or not h.endswith("d") or not h[:-1].isdigit() or int(h[:-1]) < 1
        for h in horizons
    ):
        raise ValueError("horizons must be unique positive session labels such as '5d'")
    costs = []
    for raw in cost_scenarios_bps:
        if isinstance(raw, bool):
            raise ValueError("cost scenarios must be finite non-negative numbers")
        try:
            cost = float(raw)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("cost scenarios must be finite non-negative numbers")
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("cost scenarios must be finite non-negative numbers")
        costs.append(cost)
    if not costs:
        raise ValueError("at least one cost scenario is required")

    groups = {}
    for event in events or []:
        outcomes = event.get("outcomes") or {}
        if not isinstance(outcomes, dict):
            continue
        band = score_bucket(event.get("setup_score"))
        if band is None:
            continue
        setup = str(event.get("setup_type") or "UNCLASSIFIED").upper()
        regime = str(event.get("market_regime") or "UNKNOWN").upper()
        for horizon in horizons:
            result = outcomes.get(horizon)
            if not isinstance(result, dict):
                continue
            try:
                gross = float(result.get("close_return_pct"))
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(gross):
                continue
            try:
                excess = float(result.get("excess_vs_spy_pp"))
                if not math.isfinite(excess):
                    excess = None
            except (TypeError, ValueError, OverflowError):
                excess = None
            key = (setup, band, regime, horizon)
            group = groups.setdefault(key, {"returns": [], "excess": []})
            group["returns"].append(gross)
            if excess is not None:
                group["excess"].append(excess)

    rows = []
    for (setup, band, regime, horizon), values in sorted(groups.items()):
        returns = values["returns"]
        excesses = values["excess"]
        count = len(returns)
        matched = len(excesses)
        mean_return = sum(returns) / count
        mean_excess = sum(excesses) / matched if matched else None
        row = {
            "Setup": setup,
            "Score band": band,
            "Regime": regime,
            "Horizon": horizon,
            "Signal_samples": count,
            "Benchmark_matched_samples": matched,
            "Gross_mean_return_pct": mean_return,
            "Gross_mean_excess_pp": mean_excess,
            "Return evidence": (
                f"SUPPORTED (n≥{min_return_samples})"
                if count >= min_return_samples else f"NOT SUPPORTED (n<{min_return_samples})"
            ),
            "Benchmark evidence": (
                f"SUPPORTED (n≥{min_benchmark_samples})"
                if matched >= min_benchmark_samples else f"NOT SUPPORTED (n<{min_benchmark_samples})"
            ),
        }
        for raw_cost in sorted(set(costs)):
            cost_label = str(int(raw_cost)) if raw_cost.is_integer() else str(raw_cost)
            row[f"Mean return after {cost_label}bp %"] = mean_return - raw_cost / 100.0
        row["Mean excess after 20bp pp"] = mean_excess - 0.20 if mean_excess is not None else None
        rows.append(row)
    return rows

def replay_sequence_risk_metrics(closed_events):
    """Describe loss streaks and cumulative P/L drawdown for isolated replay events.

    Events are ordered by exit_date then id. This is an event-sequence diagnostic,
    not a portfolio drawdown: replay events are independently sized and not netted.
    """
    normalized = []
    for event in closed_events or []:
        try:
            pnl = float(event.get("net_realized_pnl"))
        except (TypeError, ValueError, OverflowError):
            continue
        if not math.isfinite(pnl):
            continue
        exit_date = _parse_signal_date(event.get("exit_date"))
        if exit_date is None:
            continue
        normalized.append((exit_date, str(event.get("id") or ""), pnl))

    normalized.sort(key=lambda item: (item[0], item[1]))
    current_streak = 0
    max_streak = 0
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for _, _, pnl in normalized:
        if pnl < 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
        cumulative += pnl
        peak = max(peak, cumulative)
        max_drawdown = max(max_drawdown, peak - cumulative)

    return {
        "evaluated_events": len(normalized),
        "current_loss_streak": current_streak,
        "max_loss_streak": max_streak,
        "max_sequence_drawdown": max_drawdown,
        "ending_cumulative_pnl": cumulative,
    }



def build_volatility_transition_study(close, signal_events, *, vol_window=20, lookback=252, quantile=0.75, horizons=("1d", "5d", "10d", "20d")):
    """Measure signal outcomes by sessions since a trailing-volatility regime transition.

    Regime thresholds are calculated from prior observations only (rolling
    quantile shifted one session). Signal outcomes are precomputed observation
    fields; this helper never uses future prices to label a transition.
    """
    import pandas as pd

    if not hasattr(close, "index") or not hasattr(close, "pct_change"):
        raise ValueError("close must be a pandas Series indexed by trading session")
    if isinstance(vol_window, bool) or not isinstance(vol_window, int) or vol_window < 2:
        raise ValueError("vol_window must be an integer >= 2")
    if isinstance(lookback, bool) or not isinstance(lookback, int) or lookback < 30:
        raise ValueError("lookback must be an integer >= 30")
    try:
        quantile_value = float(quantile)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("quantile must be a finite number between 0.5 and 0.99")
    if not math.isfinite(quantile_value) or not 0.5 <= quantile_value <= 0.99:
        raise ValueError("quantile must be a finite number between 0.5 and 0.99")
    if not horizons or len(set(horizons)) != len(horizons) or any(
        not isinstance(h, str) or not h.endswith("d") or not h[:-1].isdigit() or int(h[:-1]) < 1
        for h in horizons
    ):
        raise ValueError("horizons must be unique positive session labels such as '5d'")

    prices = pd.to_numeric(close, errors="coerce").dropna().sort_index()
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]
    returns = prices.pct_change()
    realized_vol = returns.rolling(vol_window, min_periods=vol_window).std() * (252 ** 0.5) * 100
    prior_threshold = realized_vol.rolling(lookback, min_periods=lookback).quantile(quantile_value).shift(1)
    regime = pd.Series(index=prices.index, dtype="object")
    valid = realized_vol.notna() & prior_threshold.notna()
    regime.loc[valid] = ["HIGH" if value > threshold else "BASELINE"
                         for value, threshold in zip(realized_vol.loc[valid], prior_threshold.loc[valid])]
    transitions = []
    prior_state = None
    for timestamp, state in regime.items():
        if pd.isna(state):
            continue
        if prior_state is not None and state != prior_state:
            transitions.append({
                "transition_date": timestamp.date().isoformat() if hasattr(timestamp, "date") else str(timestamp),
                "from_regime": prior_state,
                "to_regime": state,
                "realized_vol_pct": float(realized_vol.loc[timestamp]),
                "prior_vol_threshold_pct": float(prior_threshold.loc[timestamp]),
            })
        prior_state = state

    session_dates = list(prices.index)
    date_positions = {str(pd.Timestamp(value).date()): i for i, value in enumerate(session_dates)}
    transition_positions = []
    for item in transitions:
        key = item["transition_date"]
        if key in date_positions:
            transition_positions.append((date_positions[key], item))

    groups = {}
    for event in signal_events or []:
        signal_date = _parse_signal_date(event.get("signal_date"))
        if signal_date is None:
            continue
        pos = date_positions.get(signal_date.isoformat())
        if pos is None:
            continue
        prior_transitions = [entry for entry in transition_positions if entry[0] <= pos]
        if not prior_transitions:
            continue
        transition_pos, transition = prior_transitions[-1]
        age = pos - transition_pos
        if age < 1 or age > 20:
            continue
        age_band = "1 session" if age == 1 else "2–5 sessions" if age <= 5 else "6–10 sessions" if age <= 10 else "11–20 sessions"
        outcomes = event.get("outcomes") or {}
        if not isinstance(outcomes, dict):
            continue
        for horizon in horizons:
            outcome = outcomes.get(horizon)
            if not isinstance(outcome, dict):
                continue
            try:
                value = float(outcome.get("close_return_pct"))
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(value):
                continue
            key = (transition["from_regime"] + " → " + transition["to_regime"], age_band, horizon,
                   str(event.get("setup_type") or "UNCLASSIFIED").upper())
            bucket = groups.setdefault(key, [])
            bucket.append(value)

    rows = []
    for (transition, age_band, horizon, setup), values in sorted(groups.items()):
        rows.append({
            "Transition": transition, "Sessions after transition": age_band,
            "Setup": setup, "Outcome horizon": horizon, "Samples": len(values),
            "Mean return %": sum(values) / len(values),
            "Win rate %": sum(value > 0 for value in values) / len(values) * 100,
            "Evidence": "Exploratory" if len(values) < 30 else "30+ observations",
        })
    return {"transitions": transitions, "rows": rows, "regime": regime, "realized_vol": realized_vol}
