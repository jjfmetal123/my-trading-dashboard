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
