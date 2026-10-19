#!/usr/bin/env python3
"""Chronological 14-calendar-day batches through June 2025; resumable state."""
import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path
import duckdb
import pandas as pd
import pandas_market_calendars as mcal
from huggingface_hub import hf_hub_download
from engine_v2 import Engine, SOURCE, START_CASH, csv_save

FIRST, LAST = date(2025, 1, 1), date(2025, 6, 30)
STATE_KEYS = ("cash", "positions", "minute_n", "loss_streak", "risk",
              "entry_minute",
              "threshold", "cooldown", "costs", "winners", "losers")
CSV_SCHEMAS = {
    "trades.csv": (["timestamp", "ticker", "side", "shares", "bar_open",
                     "execution_price", "fee", "realized_pnl", "cash_after"], "trades"),
    "equity_10min.csv": (["timestamp", "date", "equity", "cash", "holdings_json"], "snapshots"),
    "rules_1min.csv": (["timestamp", "date", "risk", "momentum_threshold",
                       "loss_streak", "winners", "losers", "equity",
                       "holdings", "pending_orders"], "minute_rules"),
    "rules_10min.csv": (["timestamp", "date", "risk", "momentum_threshold",
                        "loss_streak", "winners", "losers"], "rules"),
    "rule_events.csv": (["timestamp", "action", "reason", "loss_streak",
                         "risk", "momentum_threshold"], "rule_events"),
    "daily_equity.csv": (["date", "start_equity", "end_equity",
                          "change", "return_pct", "fills",
                          "holdings_end", "risk"], "daily"),
    "data_coverage.csv": (["date", "observed_minutes", "expected_minutes",
                           "bars"], "coverage"),
}


def restore(engine, state):
    for key in STATE_KEYS:
        if key in state:
            setattr(engine, key, state[key])
    engine.last_price = state.get("last_price", {})
    engine.previous_completed_volume = {}
    engine.pending = {symbol: 0.0 for symbol in engine.positions}
    if engine.cash < -0.01 or any(p["qty"] < 1 or p["basis"] < 0 for p in engine.positions.values()):
        raise AssertionError("Corrupt prior virtual portfolio")


def run(args):
    begin = date.fromisoformat(args.batch_start)
    end = date.fromisoformat(args.batch_end)
    if not FIRST <= begin <= end <= LAST or (end - begin).days > 30:
        raise ValueError("Must be a <=31-day batch within Jan-Jun 2025")
    base = Path(args.out)
    checkpoint = base / "state.json"
    previous = json.loads(checkpoint.read_text()) if checkpoint.is_file() else {}
    if previous:
        expected = date.fromisoformat(previous["last_batch_end"]) + timedelta(days=1)
        if end < expected:
            print("SKIP already saved " + str(begin) + ".." + str(end), flush=True)
            return
        if begin != expected:
            raise ValueError("Batch out of order: expected " + str(expected))
        if previous.get("source") != SOURCE or previous.get("strategy_version") != 2:
            raise ValueError("Incompatible checkpoint")
    elif begin != FIRST:
        raise ValueError("First batch must start 2025-01-01")
    key = begin.isoformat() + "_to_" + end.isoformat()
    batchdir = base / "batches" / key
    if batchdir.exists():
        raise FileExistsError("Uncommitted output exists: " + str(batchdir))
    engine = Engine(batchdir)
    if previous:
        restore(engine, previous)
    exchange = mcal.get_calendar("NYSE")
    scheduled = exchange.schedule(start_date=str(begin), end_date=str(end))
    if scheduled.empty:
        raise ValueError("Batch has no NYSE session")
    database = duckdb.connect()
    month = ""
    parquet = None
    peak = float(previous.get("peak_equity", START_CASH))
    maximum_drawdown = float(previous.get("max_daily_drawdown_pct", 0))
    for day_index, row in scheduled.iterrows():
        day = day_index.strftime("%Y-%m-%d")
        if day[:7] != month:
            month = day[:7]
            filename = "ohlcv_" + month + ".parquet"
            if args.local_dir:
                parquet = Path(args.local_dir) / filename
                if not parquet.is_file():
                    raise FileNotFoundError(parquet)
            else:
                parquet = Path(hf_hub_download(repo_id=SOURCE, repo_type="dataset",
                                               filename="data/" + filename))
            print("Loaded " + str(parquet), flush=True)
        opening = pd.Timestamp(row.market_open)
        closing = pd.Timestamp(row.market_close)
        bars = database.execute(
            'SELECT timestamp, UPPER(ticker) AS ticker, "open", high, low, "close", volume '
            'FROM read_parquet(?) WHERE timestamp >= ? AND timestamp < ? '
            'AND "open" > 0 AND "close" > 0 AND volume > 0 ORDER BY timestamp, ticker',
            [str(parquet), opening.to_pydatetime(), closing.to_pydatetime()]
        ).df()
        if bars.empty:
            raise RuntimeError("Missing bars for scheduled NYSE session " + day)
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        engine.session(bars, opening, closing, day)
        coverage = engine.coverage[-1]
        if coverage["observed_minutes"] < 0.95 * coverage["expected_minutes"]:
            raise RuntimeError("Incomplete minute coverage " + day)
        current = engine.equity()
        if not math.isfinite(current) or current < 0:
            raise ArithmeticError("Invalid portfolio valuation")
        peak = max(peak, current)
        maximum_drawdown = min(maximum_drawdown, (current / peak - 1) * 100)
        print(day + " equity=$" + format(current, ",.2f") +
              " fills=" + str(len(engine.trades)) +
              " minute_checks=" + str(len(engine.minute_rules)), flush=True)
    if len(engine.daily) != len(scheduled):
        raise AssertionError("Missing trading-day calculations")
    for filename, (fields, attr) in CSV_SCHEMAS.items():
        csv_save(batchdir / filename, getattr(engine, attr), fields)
    total_days = int(previous.get("sessions_completed", 0)) + len(engine.daily)
    total_trades = int(previous.get("fills_completed", 0)) + len(engine.trades)
    total_checks = int(previous.get("minute_checks_completed", 0)) + len(engine.minute_rules)
    eq = engine.equity()
    state = {name: getattr(engine, name) for name in STATE_KEYS}
    state["last_price"] = {name: engine.last_price.get(name, p["basis"] / p["qty"])
                           for name, p in engine.positions.items()}
    state["cooldown"] = {name: t for name, t in engine.cooldown.items() if t > engine.minute_n}
    state.update({"source": SOURCE, "strategy_version": 3, "last_batch_end": str(end),
                  "last_market_session": engine.daily[-1]["date"],
                  "sessions_completed": total_days, "fills_completed": total_trades,
                  "minute_checks_completed": total_checks, "peak_equity": peak,
                  "max_daily_drawdown_pct": round(maximum_drawdown, 5),
                  "equity_usd": round(eq, 2),
                  "batch_count": int(previous.get("batch_count", 0)) + 1})
    batch_summary = {
        "status": "COMPLETE_BATCH", "start": str(begin), "end": str(end),
        "sessions": len(engine.daily), "fills": len(engine.trades),
        "minute_rule_checks": len(engine.minute_rules),
        "start_equity_usd": engine.daily[0]["start_equity"],
        "end_equity_usd": round(eq, 2),
        "risk_at_end": engine.risk,
        "estimated_cumulative_trading_costs_usd": round(engine.costs, 2),
    }
    (batchdir / "batch_summary.json").write_text(json.dumps(batch_summary, indent=2) + "\n")
    all_days = len(exchange.schedule(start_date=str(FIRST), end_date=str(LAST)))
    finished = end == LAST and total_days == all_days
    summary = {
        "status": "COMPLETE" if finished else "PARTIAL",
        "source": SOURCE, "start": str(FIRST), "requested_end": str(LAST),
        "last_batch_end": str(end), "initial_capital_usd": START_CASH,
        "ending_equity_usd": round(eq, 2) if finished else None,
        "current_checkpoint_equity_usd": round(eq, 2),
        "profit_loss_usd": round(eq - START_CASH, 2) if finished else None,
        "return_pct": round((eq / START_CASH - 1) * 100, 4) if finished else None,
        "max_daily_drawdown_pct": round(maximum_drawdown, 4),
        "sessions_completed": total_days, "sessions_expected": all_days,
        "fills": total_trades, "minute_rule_checks": total_checks,
        "losing_sell_fills": engine.losers, "winning_sell_fills": engine.winners,
        "estimated_trading_costs_usd": round(engine.costs, 2),
        "positions": state["positions"], "batch_count": state["batch_count"],
        "warnings": [
            "Historic ticker universe and corporate actions may include survivorship/look-ahead bias",
            "Minute OHLCV does not simulate live spreads, order queue or market impact",
            "Signals use completed bars; executions only at next minute open",
            "Participation based on 1% of PREVIOUS bar volume; fixed 5bp slip + $0.005/share",
            "Rule logic evaluated every minute; thresholds altered only by observed outcomes",
        ],
    }
    base.mkdir(parents=True, exist_ok=True)
    (base / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    checkpoint.write_text(json.dumps(state, indent=2) + "\n")
    print("BATCH_COMPLETE " + key + " ending_equity=" + str(round(eq, 2)), flush=True)
    if finished:
        print("FINAL_JUNE_2025 " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--batch-start", required=True)
    cli.add_argument("--batch-end", required=True)
    cli.add_argument("--out", default="results/2025H1_v2")
    cli.add_argument("--local-dir", default="")
    run(cli.parse_args())
