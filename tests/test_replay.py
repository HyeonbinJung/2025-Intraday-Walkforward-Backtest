"""Small synthetic regressions. They do NOT stand in for actual 2025 history."""
import sys
import unittest
from datetime import timedelta
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from backtest import Engine
from batch_replay import restore


class CausalReplayTests(unittest.TestCase):
    def test_future_bar_is_not_used_to_fill_earlier_signal(self):
        beginning = pd.Timestamp("2025-01-02T14:30:00Z")
        rows = []
        for minute in range(40):
            px = 20.0 * 1.006 ** minute
            volume = 10000 if minute < 21 else 160000
            rows.append({"timestamp": beginning + timedelta(minutes=minute),
                         "ticker": "TEST", "open": px, "high": px * 1.002,
                         "low": px * 0.998, "close": px,
                         "volume": volume})
        bars = pd.DataFrame(rows)
        e = Engine(Path("unused_for_test"))
        features = e.score_trailing_bars(bars)
        eligible = features[features.eligible & (features.gain5 > e.threshold)]
        self.assertFalse(eligible.empty, "Fixture must generate eligible momentum")
        first_signal_minute = eligible.timestamp.min()
        e.session(bars, beginning, beginning + timedelta(minutes=40), "2025-01-02")
        buys = [x for x in e.trades if x["side"] == "BUY"]
        self.assertTrue(buys, "Fixture must generate at least one buy")
        self.assertGreater(pd.Timestamp(buys[0]["timestamp"]), first_signal_minute)
        self.assertEqual(len(e.minute_rules), 40)
        self.assertTrue(all(0 <= r["risk"] <= 0.10 for r in e.minute_rules))

    def test_restart_restores_cash_position_and_rules_but_not_future_data(self):
        saved = {"cash": 7420, "positions": {"TEST": {"qty": 2, "basis": 200, "peak": 105}},
                 "last_price": {"TEST": 103},
                 "minute_n": 360, "loss_streak": 3, "risk": 0.04,
                 "threshold": 0.007, "cooldown": {"TEST": 361},
                 "costs": 20.2, "winners": 8, "losers": 11}
        engine = Engine(Path("unused_for_test"))
        engine.previous_completed_volume = {"TEST": 1000000}
        restore(engine, saved)
        self.assertEqual(engine.cash, 7420)
        self.assertEqual(engine.risk, 0.04)
        self.assertEqual(engine.pending, {"TEST": 0.0})
        self.assertEqual(engine.previous_completed_volume, {})
        self.assertAlmostEqual(engine.equity(), 7626)


if __name__ == "__main__":
    unittest.main()
