import unittest
from validation_diagnostics import deoverlap_events, score_bucket, full_history_display_state


class ValidationDiagnosticsTests(unittest.TestCase):
    def test_full_history_available_payload_requires_configurations(self):
        state = full_history_display_state({
            "status": "AVAILABLE",
            "configurations": [{"configuration": "BASELINE"}],
            "transition_date_displacement": [{"configuration": "ALT", "status": "NO_MATCHED_TRANSITIONS"}],
            "authority": "NONE",
            "decision_authority": "NONE",
        })
        self.assertTrue(state["available"])
        self.assertEqual(state["configuration_count"], 1)
        self.assertEqual(state["displacement_count"], 1)
        self.assertEqual(state["authority"], "NONE")
        self.assertEqual(state["decision_authority"], "NONE")

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
        state = full_history_display_state({
            "status": "AVAILABLE",
            "configurations": [{"configuration": "BASELINE"}],
            "transition_date_displacement": [{
                "configuration": "ALT", "status": "NO_MATCHED_TRANSITIONS"
            }],
        })
        self.assertTrue(state["available"])
        self.assertEqual(state["displacement_count"], 1)

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
