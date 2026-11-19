import unittest
from validation_diagnostics import deoverlap_events, score_bucket


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
        self.assertEqual(kept[0]["signal_date"], "2025-01-02")

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


if __name__ == "__main__":
    unittest.main()
