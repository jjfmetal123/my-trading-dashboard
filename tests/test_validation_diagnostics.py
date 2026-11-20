import unittest
from validation_diagnostics import (deoverlap_events, score_bucket, full_history_display_state, full_history_display_rows)


def valid_full_history_payload():
    return {
        "status": "AVAILABLE",
        "baseline_configuration": "BASELINE",
        "configurations": [{
            "configuration": "BASELINE",
            "session_count": 100,
            "known_session_count": 90,
            "unknown_session_count": 10,
            "regime_occupancy_pct": {"LOW": 25.0, "NORMAL": 50.0, "HIGH": 25.0},
            "transition_counts": {
                "LOW_TO_HIGH": 2, "HIGH_TO_LOW": 1, "LOW_TO_NORMAL": 3,
                "NORMAL_TO_LOW": 4, "NORMAL_TO_HIGH": 5, "HIGH_TO_NORMAL": 6,
            },
        }],
        "transition_date_displacement": [{
            "configuration": "ALTERNATIVE",
            "max_match_shift_sessions": 20,
            "matched_baseline_transitions": 8,
            "unmatched_baseline_transitions": 2,
            "unmatched_alternative_transitions": 1,
            "median_absolute_session_shift": 3.5,
            "maximum_absolute_session_shift": 9,
            "median_signed_session_shift": -1.0,
            "status": "AVAILABLE",
        }],
        "method": "FULL_AVAILABLE_SPY_SESSION_HISTORY_POINT_IN_TIME_NO_RETURN_BASED_SELECTION",
        "history_start_date": "1993-01-29",
        "history_end_date": "2026-11-20",
        "history_period": "max",
        "stable_market_session_index": True,
        "authority": "NONE",
        "decision_authority": "NONE",
    }


class ValidationDiagnosticsTests(unittest.TestCase):
    def test_full_history_worker_contract_maps_to_dashboard_rows(self):
        display = full_history_display_rows(valid_full_history_payload())
        self.assertTrue(display["state"]["available"])
        self.assertEqual(display["baseline_configuration"], "BASELINE")
        self.assertEqual(display["state"]["history_start_date"], "1993-01-29")
        self.assertEqual(display["state"]["history_end_date"], "2026-11-20")
        self.assertEqual(display["state"]["history_period"], "max")
        self.assertTrue(display["state"]["stable_market_session_index"])
        self.assertEqual(display["occupancy_rows"][0]["Known / unknown"], "90 / 10")
        self.assertEqual(display["occupancy_rows"][0]["LOW / NORMAL / HIGH (%)"], "25.0 / 50.0 / 25.0")
        self.assertEqual(display["occupancy_rows"][0]["NORMAL→HIGH"], 5)
        self.assertEqual(display["displacement_rows"][0]["Match window (sessions)"], 20)
        self.assertEqual(display["displacement_rows"][0]["Unmatched baseline / alternative"], "2 / 1")
        self.assertEqual(display["displacement_rows"][0]["Median signed shift (sessions)"], -1.0)
        self.assertEqual(display["state"]["authority"], "NONE")
        self.assertEqual(display["state"]["decision_authority"], "NONE")

    def test_full_history_waiting_for_signal_metadata(self):
        state = full_history_display_state({
            "status": "WAITING_FOR_SIGNAL_HISTORY_METADATA",
            "authority": "NONE",
            "decision_authority": "NONE",
        })
        self.assertFalse(state["available"])
        self.assertEqual(state["status"], "WAITING_FOR_SIGNAL_HISTORY_METADATA")
        self.assertEqual(state["configuration_count"], 0)

    def test_full_history_no_matched_transitions_keeps_occupancy_available(self):
        payload = valid_full_history_payload()
        payload["transition_date_displacement"][0]["status"] = "NO_MATCHED_TRANSITIONS"
        payload["transition_date_displacement"][0]["matched_baseline_transitions"] = 0
        display = full_history_display_rows(payload)
        self.assertTrue(display["state"]["available"])
        self.assertEqual(display["state"]["displacement_count"], 1)
        self.assertEqual(display["displacement_rows"][0]["Status"], "NO_MATCHED_TRANSITIONS")

    def test_full_history_missing_authority_or_worker_fields_fails_closed(self):
        payload = valid_full_history_payload()
        payload.pop("decision_authority")
        self.assertFalse(full_history_display_state(payload)["available"])
        payload = valid_full_history_payload()
        payload["configurations"][0].pop("transition_counts")
        self.assertFalse(full_history_display_state(payload)["available"])
        payload = valid_full_history_payload()
        payload.pop("transition_date_displacement")
        self.assertFalse(full_history_display_state(payload)["available"])

    def test_full_history_absent_nested_field_fails_closed(self):
        evidence_report = {"status": "COMPLETE"}
        payload = evidence_report.get("volatility_classification_sensitivity", {}).get("full_history")
        state = full_history_display_state(payload)
        self.assertFalse(state["available"])
        self.assertEqual(state["status"], "MISSING_PAYLOAD")
        self.assertEqual(state["authority"], "NONE")
        self.assertEqual(state["decision_authority"], "NONE")

    def test_full_history_available_without_configurations_is_not_available(self):
        state = full_history_display_state({"status": "AVAILABLE", "configurations": []})
        self.assertFalse(state["available"])
        self.assertEqual(state["configuration_count"], 0)

    def test_score_buckets_match_worker_boundaries(self):
        self.assertEqual(score_bucket(0), "00-49")
        self.assertEqual(score_bucket(49.9), "00-49")
        self.assertEqual(score_bucket(50), "50-59")
        self.assertEqual(score_bucket(89.9), "80-89")
        self.assertEqual(score_bucket(90), "90-100")
        self.assertEqual(score_bucket(100), "90-100")
        self.assertIsNone(score_bucket(None))
        self.assertIsNone(score_bucket(float("nan")))

    def test_deoverlap_respects_symbol_setup_and_cooldown(self):
        events = [
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "2025-01-02"},
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "2025-01-03"},
            {"symbol": "AAA", "setup_type": "BREAKOUT", "signal_date": "2025-01-03"},
            {"symbol": "BBB", "setup_type": "PULLBACK", "signal_date": "2025-01-03"},
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "2025-01-31"},
        ]
        kept = deoverlap_events(events, cooldown_sessions=20)
        self.assertEqual(len(kept), 4)
        self.assertIn("2025-01-02", [event["signal_date"] for event in kept])

    def test_invalid_dates_skipped_and_zero_cooldown_keeps_all_valid(self):
        events = [
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "bad-date"},
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "2025-01-02"},
            {"symbol": "AAA", "setup_type": "PULLBACK", "signal_date": "2025-01-03"},
        ]
        self.assertEqual(len(deoverlap_events(events, cooldown_sessions=0)), 2)

    def test_invalid_cooldown_rejected(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    deoverlap_events([], cooldown_sessions=value)

    def test_edge_diagnostics_separate_signal_and_benchmark_support(self):
        from validation_diagnostics import build_edge_diagnostics
        events = []
        for index in range(3):
            events.append({
                "symbol": f"SYM{index}", "setup_type": "PULLBACK WATCH",
                "setup_score": 93, "market_regime": "BULL",
                "outcomes": {"5d": {
                    "close_return_pct": 1.0 + index,
                    "excess_vs_spy_pp": 0.5 if index == 0 else None,
                }},
            })
        rows = build_edge_diagnostics(
            events, min_return_samples=3, min_benchmark_samples=2
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["Score band"], "90-100")
        self.assertEqual(row["Signal_samples"], 3)
        self.assertEqual(row["Benchmark_matched_samples"], 1)
        self.assertEqual(row["Return evidence"], "SUPPORTED (n≥3)")
        self.assertEqual(row["Benchmark evidence"], "NOT SUPPORTED (n<2)")
        self.assertAlmostEqual(row["Gross_mean_return_pct"], 2.0)
        self.assertAlmostEqual(row["Mean return after 20bp %"], 1.8)
        self.assertAlmostEqual(row["Mean excess after 20bp pp"], 0.3)

    def test_edge_diagnostics_ignore_invalid_returns_and_reject_bad_config(self):
        from validation_diagnostics import build_edge_diagnostics
        events = [{
            "setup_type": "BREAKOUT WATCH", "setup_score": 80,
            "outcomes": {"5d": {"close_return_pct": "nan", "excess_vs_spy_pp": 1.0}},
        }]
        self.assertEqual(build_edge_diagnostics(events), [])
        for kwargs in (
            {"min_return_samples": 0},
            {"min_benchmark_samples": True},
            {"horizons": ("5d", "5d")},
            {"cost_scenarios_bps": (-1,)},
            {"cost_scenarios_bps": ()},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    build_edge_diagnostics([], **kwargs)


if __name__ == "__main__":
    unittest.main()
