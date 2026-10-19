#!/usr/bin/env python3
"""2025 no-lookahead US-equity 1-minute paper trading replay."""
import argparse
import csv
import json
import math
from collections import defaultdict, deque
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from huggingface_hub import hf_hub_download

START_CASH = 100000.0
SOURCE = "mito0o852/OHLCV-1m"
SLIP = 0.0005
COMMISSION = 0.005
PARTICIPATION = 0.01


def csv_save(path, entries, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(entries)


class Engine:
    def __init__(self, output):
        self.output = Path(output)
        self.cash = START_CASH
        self.positions = {}
        self.last_price = {}
        self.pending = {}
        self.minute_n = 0
        self.loss_streak = 0
        self.risk = 0.10
        self.threshold = 0.004
        self.cooldown = {}
        self.trades = []
        self.snapshots = []
        self.rules = []
        self.rule_events = []
        self.daily = []
        self.coverage = []
        self.costs = 0.0
        self.winners = 0
        self.losers = 0

    def equity(self):
        return self.cash + sum(p["qty"] * self.last_price.get(symbol, p["basis"] / p["qty"])
                               for symbol, p in self.positions.items())

    def event(self, when, action, reason):
        self.rule_events.append({"timestamp": when, "action": action,
                                 "reason": reason, "loss_streak": self.loss_streak,
                                 "risk": round(self.risk, 6),
                                 "momentum_threshold": round(self.threshold, 6)})

    def realized(self, symbol, pnl, when):
        if pnl < 0:
            self.losers += 1
            self.loss_streak += 1
            self.cooldown[symbol] = self.minute_n + min(60, self.loss_streak * 6)
            self.risk = max(0.03, 0.10 * 0.8 ** min(self.loss_streak, 6))
            self.threshold = min(0.018, 0.004 + self.loss_streak * 0.001)
            self.event(when, "TIGHTEN_AFTER_LOSS", symbol + " loss=" + str(round(pnl, 2)))
        elif pnl > 0:
            self.winners += 1
            if self.loss_streak:
                self.loss_streak -= 1
                self.risk = max(0.03, 0.10 * 0.8 ** min(self.loss_streak, 6))
                self.threshold = min(0.018, 0.004 + self.loss_streak * 0.001)
                self.event(when, "RECOVER_AFTER_GAIN", symbol + " gain=" + str(round(pnl, 2)))

    def execute(self, symbol, goal_usd, op, vol, when):
        if op <= 0 or vol <= 0:
            return
        pos = self.positions.get(symbol)
        old_qty = pos["qty"] if pos else 0
        target_qty = max(0, int(goal_usd / op))
        difference = target_qty - old_qty
        max_qty = math.floor(vol * PARTICIPATION)
        amount = min(abs(difference), max_qty)
        if amount <= 0:
            return
        side = "BUY" if difference > 0 else "SELL"
        price = op * (1 + SLIP if side == "BUY" else 1 - SLIP)
        if side == "BUY":
            amount = min(amount, int(self.cash / (price + COMMISSION)))
        if amount <= 0:
            return
        fee = amount * COMMISSION
        self.costs += fee + amount * abs(price - op)
        realized = 0.0
        if side == "BUY":
            cost = amount * price + fee
            self.cash -= cost
            if pos:
                pos["basis"] += cost
                pos["qty"] += amount
                pos["peak"] = max(pos["peak"], op)
            else:
                self.positions[symbol] = {"qty": amount, "basis": cost, "peak": op}
        else:
            basis = pos["basis"] * amount / pos["qty"]
            realized = amount * price - fee - basis
            self.cash += amount * price - fee
            pos["qty"] -= amount
            pos["basis"] -= basis
            if pos["qty"] <= 0:
                del self.positions[symbol]
                self.realized(symbol, realized, when)
        self.trades.append({"timestamp": when, "ticker": symbol, "side": side,
                            "shares": amount, "bar_open": round(op, 5),
                            "execution_price": round(price, 5), "fee": round(fee, 4),
                            "realized_pnl": round(realized, 4),
                            "cash_after": round(self.cash, 2)})

    def rank(self, history, timestamp):
        ranked = []
        for ticker, h in history.items():
            if len(h) < 21 or self.cooldown.get(ticker, 0) > self.minute_n:
                continue
            if (timestamp - h[0][0]).total_seconds() != 1200:
                continue
            c = np.array([z[1] for z in h])
            v = np.array([z[2] for z in h])
            if np.min(c) <= 0 or not 2 <= c[-1] <= 1000:
                continue
            gain5 = c[-1] / c[-6] - 1
            gain20 = c[-1] / c[0] - 1
            rel_vol = np.mean(v[-5:]) / max(np.mean(v[-20:-5]), 1)
            avg_dv = np.mean(c[-20:] * v[-20:])
            if gain5 < self.threshold or rel_vol < 1.15 or avg_dv < 200000:
                continue
            volatility = np.std(np.diff(np.log(c[-11:])))
            score = 4 * gain5 + 2 * max(0, gain20) + volatility + 0.002 * np.log1p(rel_vol)
            ranked.append((score, ticker))
        ranked.sort(reverse=True)
        return [sym for _, sym in ranked[:5]]

    def session(self, frame, open_time, close_time, date):
        start = self.equity()
        prior_count = len(self.trades)
        history = defaultdict(lambda: deque(maxlen=21))
        # A decision at 15:58 close exits at 15:59 open, not hindsight 15:59 close.
        flatten_signal_time = close_time - pd.Timedelta(minutes=2)
        observed = 0
        frame = frame.drop_duplicates(["timestamp", "ticker"], keep="last")
        for timestamp, group in frame.groupby("timestamp", sort=True):
            timestamp = pd.Timestamp(timestamp)
            when = timestamp.isoformat()
            current = {r.ticker: r for r in group.itertuples(index=False)
                       if r.open > 0 and r.close > 0 and r.volume > 0}
            if not current:
                continue
            observed += 1
            self.minute_n += 1
            old_orders = self.pending
            self.pending = {}
            # Sell first, buy second. Order submitted after last bar's close.
            for symbol in sorted(old_orders, key=lambda x: old_orders[x]):
                if symbol in current:
                    b = current[symbol]
                    self.execute(symbol, old_orders[symbol], float(b.open),
                                 float(b.volume), when)
                elif symbol in self.positions:
                    self.pending[symbol] = 0.0  # no synthetic fill for missing candles
            for symbol, b in current.items():
                self.last_price[symbol] = float(b.close)
                history[symbol].append((timestamp, float(b.close), float(b.volume)))
                if symbol in self.positions:
                    self.positions[symbol]["peak"] = max(self.positions[symbol]["peak"],
                                                          float(b.close))
            if timestamp >= flatten_signal_time:
                next_orders = {sym: 0.0 for sym in self.positions}
            else:
                selected = self.rank(history, timestamp)
                next_orders = {sym: 0.0 for sym in self.positions if sym not in selected}
                equity = self.equity()
                for sym in selected:
                    position = self.positions.get(sym)
                    if position:
                        basis_per_share = position["basis"] / position["qty"]
                        if (self.last_price[sym] < basis_per_share * 0.985 or
                                self.last_price[sym] < position["peak"] * 0.98):
                            next_orders[sym] = 0.0
                            self.cooldown[sym] = self.minute_n + 10
                            self.event(when, "STOP_QUEUED", sym)
                            continue
                    next_orders[sym] = equity * self.risk
            self.pending.update(next_orders)
            eastern_time = timestamp.tz_convert("America/New_York")
            if eastern_time.minute % 10 == 0 or timestamp == close_time - pd.Timedelta(minutes=1):
                self.snapshots.append({"timestamp": when, "date": date,
                                       "equity": round(self.equity(), 2),
                                       "cash": round(self.cash, 2),
                                       "holdings_json": json.dumps({k: v["qty"] for k, v
                                                                    in sorted(self.positions.items())})})
                self.rules.append({"timestamp": when, "date": date,
                                   "risk": round(self.risk, 6),
                                   "momentum_threshold": round(self.threshold, 6),
                                   "loss_streak": self.loss_streak,
                                   "winners": self.winners, "losers": self.losers})
        ended = self.equity()
        self.daily.append({"date": date, "start_equity": round(start, 2),
                           "end_equity": round(ended, 2),
                           "change": round(ended - start, 2),
                           "return_pct": round((ended / start - 1) * 100, 4) if start else 0,
                           "fills": len(self.trades) - prior_count,
                           "holdings_end": len(self.positions), "risk": round(self.risk, 6)})
        self.coverage.append({"date": date, "observed_minutes": observed,
                              "expected_minutes": int((close_time - open_time).total_seconds() / 60),
                              "bars": len(frame)})
        # If a ticker has no last-minute print, holding it overnight is recorded,
        # never marked as an imaginary closing fill. Next session sells at open.
        self.pending = {sym: 0.0 for sym in self.positions}

    def save(self, status, error=""):
        out = self.output
        csv_save(out / "trades.csv", self.trades,
                 ["timestamp", "ticker", "side", "shares", "bar_open", "execution_price",
                  "fee", "realized_pnl", "cash_after"])
        csv_save(out / "equity_10min.csv", self.snapshots,
                 ["timestamp", "date", "equity", "cash", "holdings_json"])
        csv_save(out / "rules_10min.csv", self.rules,
                 ["timestamp", "date", "risk", "momentum_threshold", "loss_streak", "winners", "losers"])
        csv_save(out / "rule_events.csv", self.rule_events,
                 ["timestamp", "action", "reason", "loss_streak", "risk", "momentum_threshold"])
        csv_save(out / "daily_equity.csv", self.daily,
                 ["date", "start_equity", "end_equity", "change", "return_pct",
                  "fills", "holdings_end", "risk"])
        csv_save(out / "data_coverage.csv", self.coverage,
                 ["date", "observed_minutes", "expected_minutes", "bars"])
        equity = self.equity()
        eq = np.array([x["end_equity"] for x in self.daily])
        max_dd = float(np.min(eq / np.maximum.accumulate(eq) - 1) * 100) if len(eq) else None
        summary = {"status": status, "error": error, "source": SOURCE,
                   "start_date": "2025-01-01", "end_date": "2025-12-31",
                   "starting_capital_usd": START_CASH,
                   "ending_equity_usd": round(equity, 2) if status == "COMPLETE" else None,
                   "ending_cash_usd": round(self.cash, 2) if status == "COMPLETE" else None,
                   "return_pct": round((equity / START_CASH - 1) * 100, 4)
                   if status == "COMPLETE" else None,
                   "max_daily_drawdown_pct": round(max_dd, 4) if max_dd is not None else None,
                   "trading_sessions": len(self.daily), "fills": len(self.trades),
                   "winners": self.winners, "losers": self.losers,
                   "costs_estimate_usd": round(self.costs, 2),
                   "remaining_positions": self.positions,
                   "notes": ["True 1-min decision cycle; next-minute open fills",
                             "Universe limited to source coverage, possible delisting bias",
                             "Third-party Finnhub-origin historic parquet, potentially ex-post adjusted",
                             "Only 1 percent of each candle volume tradable",
                             "Slippage 5 bps each side and commission 0.005 USD per share"]}
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/2025")
    parser.add_argument("--local-dir", default="")
    args = parser.parse_args()
    engine = Engine(args.out)
    schedule = mcal.get_calendar("NYSE").schedule(start_date="2025-01-01", end_date="2025-12-31")
    db = duckdb.connect()
    month = None
    file_path = None
    try:
        for date, s in schedule.iterrows():
            day = date.strftime("%Y-%m-%d")
            if day[:7] != month:
                month = day[:7]
                name = "ohlcv_" + month + ".parquet"
                if args.local_dir:
                    file_path = Path(args.local_dir) / name
                    if not file_path.is_file():
                        raise FileNotFoundError(str(file_path))
                else:
                    file_path = Path(hf_hub_download(repo_id=SOURCE, repo_type="dataset",
                                                     filename="data/" + name))
                print("Downloaded/located " + name, flush=True)
            open_time = pd.Timestamp(s.market_open)
            close_time = pd.Timestamp(s.market_close)
            frame = db.execute(
                'SELECT timestamp, UPPER(ticker) AS ticker, "open", high, low, "close", volume '
                'FROM read_parquet(?) WHERE timestamp >= ? AND timestamp < ? '
                'AND "open" > 0 AND "close" > 0 AND volume > 0 ORDER BY timestamp, ticker',
                [str(file_path), open_time.to_pydatetime(), close_time.to_pydatetime()]).df()
            if frame.empty:
                raise RuntimeError("No market bars for expected session " + day)
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
            engine.session(frame, open_time, close_time, day)
            print(day + " equity " + str(round(engine.equity(), 2)) +
                  " fills " + str(len(engine.trades)), flush=True)
        engine.save("COMPLETE")
        print("COMPLETE " + str(engine.output / "summary.json"), flush=True)
    except Exception as exc:
        engine.save("INCOMPLETE", repr(exc))
        raise


if __name__ == "__main__":
    main()
