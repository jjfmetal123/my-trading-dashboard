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



def _valid_full_history_configurations(payload):
    raw = payload.get("configurations") if isinstance(payload, dict) else None
    rows = raw if isinstance(raw, list) else []
    return [
        row for row in rows
        if isinstance(row, dict)
        and row.get("configuration")
        and isinstance(row.get("regime_occupancy_pct"), dict)
        and isinstance(row.get("transition_counts"), dict)
        and all(
            isinstance(row.get(field), (int, float))
            and not isinstance(row.get(field), bool)
            and math.isfinite(float(row[field]))
            and row[field] >= 0
            for field in ("session_count", "known_session_count", "unknown_session_count")
        )
    ]


def full_history_display_state(payload):
    """Validate the persisted worker contract before showing full-history evidence."""
    unavailable = {
        "status": "MISSING_PAYLOAD", "available": False,
        "configuration_count": 0, "displacement_count": 0,
        "authority": "NONE", "decision_authority": "NONE",
    }
    if not isinstance(payload, dict):
        return unavailable
    status = str(payload.get("status") or "UNKNOWN").upper()
    configurations = _valid_full_history_configurations(payload)
    raw_displacement = payload.get("transition_date_displacement")
    displacement = raw_displacement if isinstance(raw_displacement, list) else []
    displacement = [row for row in displacement if isinstance(row, dict)]
    authority = str(payload.get("authority") or "UNDECLARED").upper()
    decision_authority = str(payload.get("decision_authority") or "UNDECLARED").upper()
    baseline = str(payload.get("baseline_configuration") or "")
    baseline_present = any(row.get("configuration") == baseline for row in configurations)
    available = (
        status == "AVAILABLE"
        and bool(configurations)
        and baseline_present
        and isinstance(raw_displacement, list)
        and authority == "NONE"
        and decision_authority == "NONE"
    )
    return {
        "status": status if status else "UNKNOWN",
        "available": available,
        "configuration_count": len(configurations),
        "displacement_count": len(displacement),
        "authority": authority,
        "decision_authority": decision_authority,
    }


def full_history_display_rows(payload):
    """Map the exact worker payload into dashboard table rows after contract validation."""
    state = full_history_display_state(payload)
    if not state["available"]:
        return {"state": state, "occupancy_rows": [], "displacement_rows": []}
    occupancy_rows = []
    for item in _valid_full_history_configurations(payload):
        occupancy = item["regime_occupancy_pct"]
        transitions = item["transition_counts"]
        occupancy_rows.append({
            "Definition": item.get("configuration"),
            "Sessions": item.get("session_count"),
            "Known / unknown": f'{item.get("known_session_count")} / {item.get("unknown_session_count")}',
            "LOW / NORMAL / HIGH (%)": " / ".join(
                str(occupancy.get(label)) if occupancy.get(label) is not None else "—"
                for label in ("LOW", "NORMAL", "HIGH")
            ),
            "LOW→HIGH": transitions.get("LOW_TO_HIGH", 0),
            "HIGH→LOW": transitions.get("HIGH_TO_LOW", 0),
            "LOW→NORMAL": transitions.get("LOW_TO_NORMAL", 0),
            "NORMAL→LOW": transitions.get("NORMAL_TO_LOW", 0),
            "NORMAL→HIGH": transitions.get("NORMAL_TO_HIGH", 0),
            "HIGH→NORMAL": transitions.get("HIGH_TO_NORMAL", 0),
        })
    displacement_rows = []
    for item in payload["transition_date_displacement"]:
        if not isinstance(item, dict):
            continue
        displacement_rows.append({
            "Alternative definition": item.get("configuration"),
            "Match window (sessions)": item.get("max_match_shift_sessions"),
            "Matched baseline transitions": item.get("matched_baseline_transitions"),
            "Unmatched baseline / alternative": (
                f'{item.get("unmatched_baseline_transitions", 0)} / '
                f'{item.get("unmatched_alternative_transitions", 0)}'
            ),
            "Median absolute shift (sessions)": item.get("median_absolute_session_shift"),
            "Maximum absolute shift (sessions)": item.get("maximum_absolute_session_shift"),
            "Median signed shift (sessions)": item.get("median_signed_session_shift"),
            "Status": item.get("status"),
        })
    return {
        "state": state,
        "baseline_configuration": payload.get("baseline_configuration"),
        "occupancy_rows": occupancy_rows,
        "displacement_rows": displacement_rows,
    }

def build_edge_diagnostics(
    events,
    *,
    horizons=("5d", "10d", "20d"),
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
