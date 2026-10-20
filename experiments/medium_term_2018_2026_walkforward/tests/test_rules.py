"""Unit checks for chronology, next-open exits and strict-input fail-closed."""
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtest import (END, PROFILE_BY_NAME, PointInTimeGates, account,
                      evaluate_shadow, selection_schedule, step)


class HistoricalRulesTest(unittest.TestCase):
    def test_selection_only_at_historical_boundaries(self):
        days = pd.bdate_range("2018-01-02", "2026-06-30")
        schedule = selection_schedule(days)
        self.assertEqual(schedule[pd.Timestamp("2018-01-02")][0], "INITIAL_DEVELOPMENT")
        self.assertEqual(schedule[pd.Timestamp("2019-01-01")][0], "JANUARY_ANNUAL_REVIEW")
        self.assertEqual(schedule[pd.Timestamp("2019-07-01")][0], "2019H1_FORWARD_REVIEW")
        self.assertNotIn(pd.Timestamp("2026-01-01"), schedule)

    def test_shadow_evaluation_ignores_data_outside_window(self):
        old = [{"equity": 100_000 + n * 500} for n in range(90)]
        old_score = evaluate_shadow(old, 60)
        self.assertEqual(old_score, evaluate_shadow(old[-60:], 60))
        self.assertNotEqual(old_score, evaluate_shadow(old[:-1], 60))

    def fixture(self, fill):
        dates = pd.to_datetime(["2025-12-29", "2025-12-30", "2025-12-31",
                                "2026-06-29", "2026-06-30"])
        p = pd.DataFrame({"ABC": [100., 105., 111., 112., 113.],
                          "SPY": [400., 401., 402., 403., 404.]}, index=dates)
        op = p.copy()
        op.loc[pd.Timestamp("2026-06-30"), "ABC"] = fill
        f = {"sma200": pd.DataFrame({"SPY": [390.] * len(dates)}, index=dates)}
        return p, op, f

    def test_take_profit_sells_at_next_open_not_prior_close(self):
        p, op, f = self.fixture(115.0)
        state = account()
        state["cash"] = 90_000
        state["held"]["ABC"] = {"qty": 100., "entry": 100., "date": pd.Timestamp("2025-12-31"),
                                 "peak": 112., "last": 112., "cost": 10_006.,
                                 "profile": "balanced", "untradeable": 0}
        d = pd.Timestamp(END)
        step(state, d, pd.Timestamp("2026-06-29"), PROFILE_BY_NAME["balanced"], [],
             p, op, f, lambda _date: frozenset({"ABC", "SPY"}), set(), False)
        self.assertEqual(len(state["held"]), 0)
        self.assertEqual(state["trades"][-1]["side"], "SELL")
        self.assertEqual(state["trades"][-1]["price"], 115.0)
        self.assertEqual(state["trades"][-1]["reason"], "FORCED_JUNE_2026")

    def test_non_executable_liquidation_is_writeoff_not_sell(self):
        p, op, f = self.fixture(float("nan"))
        state = account()
        state["cash"] = 90_000
        state["held"]["ABC"] = {"qty": 100., "entry": 100., "date": pd.Timestamp("2025-12-31"),
                                 "peak": 112., "last": 112., "cost": 10_006.,
                                 "profile": "balanced", "untradeable": 0}
        d = pd.Timestamp(END)
        step(state, d, pd.Timestamp("2026-06-29"), PROFILE_BY_NAME["balanced"], [],
             p, op, f, lambda _date: frozenset({"ABC", "SPY"}), set(), False)
        self.assertEqual(state["nonexec_writeoffs"], 1)
        self.assertEqual(state["trades"][-1]["side"], "NON_EXECUTABLE_WRITEOFF")
        self.assertEqual(state["cash"], 90_000)

    def test_strict_refuses_unpopulated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            with self.assertRaises(ValueError):
                PointInTimeGates("strict", d / "none.csv", d / "none2.csv")


if __name__ == "__main__":
    unittest.main()
