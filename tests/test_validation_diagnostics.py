import unittest
from validation_diagnostics import build_volatility_transition_study, deoverlap_events, replay_sequence_risk_metrics, score_bucket


class ValidationDiagnosticsTests(unittest.TestCase):
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


    def test_replay_sequence_risk_metrics_orders_events_and_resets_streak(self):
        events = [
            {"id": "c", "exit_date": "2025-01-03", "net_realized_pnl": 5},
            {"id": "a", "exit_date": "2025-01-01", "net_realized_pnl": -10},
            {"id": "b", "exit_date": "2025-01-02", "net_realized_pnl": -20},
            {"id": "d", "exit_date": "2025-01-04", "net_realized_pnl": -3},
            {"id": "bad", "exit_date": "bad-date", "net_realized_pnl": -100},
        ]
        metrics = replay_sequence_risk_metrics(events)
        self.assertEqual(metrics["evaluated_events"], 4)
        self.assertEqual(metrics["current_loss_streak"], 1)
        self.assertEqual(metrics["max_loss_streak"], 2)
        self.assertAlmostEqual(metrics["max_sequence_drawdown"], 30)
        self.assertAlmostEqual(metrics["ending_cumulative_pnl"], -28)

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
        # One-session outcomes are supported alongside the existing 5/10/20-session horizons.
        events[0]["outcomes"]["1d"] = {"close_return_pct": 0.25, "excess_vs_spy_pp": 0.10}
        rows = build_edge_diagnostics(
            events, horizons=("1d", "5d"), min_return_samples=3, min_benchmark_samples=2
        )
        one_day = next(row for row in rows if row["Horizon"] == "1d")
        self.assertEqual(one_day["Signal_samples"], 1)
        self.assertAlmostEqual(one_day["Gross_mean_return_pct"], 0.25)
        self.assertEqual(len(rows), 2)
        five_day = next(row for row in rows if row["Horizon"] == "5d")
        row = five_day
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


    def test_volatility_transition_uses_prior_only_threshold_and_buckets_signal_age(self):
        import pandas as pd
        from validation_diagnostics import build_volatility_transition_study
        index = pd.bdate_range("2023-01-02", periods=180)
        # Quiet returns followed by a sustained high-volatility shock.
        returns = [0.001 if i % 2 else -0.001 for i in range(180)]
        for i in range(100, 180):
            returns[i] = 0.035 if i % 2 else -0.035
        prices = [100.0]
        for value in returns[1:]:
            prices.append(prices[-1] * (1 + value))
        close = pd.Series(prices, index=index)
        transition_date = index[100].date().isoformat()
        events = [{
            "signal_date": index[101].date().isoformat(), "setup_type": "PULLBACK",
            "outcomes": {"1d": {"close_return_pct": 1.0}, "5d": {"close_return_pct": 2.0}},
        }]
        result = build_volatility_transition_study(close, events, vol_window=10, lookback=60)
        self.assertTrue(result["transitions"])
        self.assertEqual(result["transitions"][0]["transition_date"], transition_date)
        self.assertEqual(result["transitions"][0]["to_regime"], "HIGH")
        self.assertEqual(len(result["rows"]), 2)
        self.assertTrue(all(row["Sessions after transition"] == "1 session" for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
