# 2025 January–June intraday trading replay — $100,000 virtual capital

**Period:** January 1 to June 30, 2025, NYSE regular-market sessions only. **Batch size:** consecutive 14-calendar-day windows (about 10 trading sessions). **Simulation cadence:** new market assessment and risk-rule evaluation after every completed 1-minute OHLCV candle. **Position target reevaluation every minute**; an actual order executes only if the signals, risk limits and available data justify it.

## Status and final balance

Current auditable result: `results/2025H1/summary.json`. A final June balance is reported **only if** that file has `"status": "COMPLETE"` and its sessions completed match the NYSE calendar count through June 30. Earlier batch files deliberately say `PARTIAL`. The earlier full-year attempts have been superseded, and their reported January figures are not part of the definitive Jan–Jun result.

**Actions workflow:** [2025H1 replay](../../actions/workflows/replay-2025.yml). Runs independently on the GitHub-hosted computer and commits each completed two-week historical batch to the public repository before starting the next. After interruptions, it resumes with the cash, positions and rules from the last committed batch, rather than resetting to $100,000.

## Minute-by-minute execution

1. Use only OHLCV bars with timestamps already fully completed by the decision minute; rolling features are backward-looking.
2. Each minute rank up to five eligible momentum + relative-volume equities from that minute's available universe.
3. Reevaluate stop/exit/entry and target positions every minute; fill **no earlier than the next minute's opening print**. Initial minute cannot fill using its own as-yet-unobserved volume.
4. Buy/sell size capped by **1% of the PREVIOUS completed minute's recorded volume**, estimated adverse slippage **5 bps per side** plus **$0.005 per share** fees. No leverage, shorts or borrowing.
5. Every completed minute evaluate defensive rule conditions and record current risk/threshold, holdings count and account value in `rules_1min.csv`. Parameters change **only when triggered** by realized losses or profitable exits, rather than magically changing on every clock tick. Losing sell fills reduce future position budget, increase momentum hurdle and impose symbol cooldowns.
6. Save a position/equity and rule snapshot every 10 minutes, every transaction, rule-change event, daily equity, observed-minute coverage, and one JSON batch summary for **each** 14-day chunk.
7. At each completed batch checkpoint, persist cash, holdings, last available marks, minute counter, risk fraction, momentum threshold, loss streak, costs and cooldowns, then commit the auditable outputs.

## Directory structure

- `src/backtest.py` — historical trading engine, minute-by-minute rule and portfolio decisions.
- `src/batch_replay.py` — Jan–Jun time windows, explicit resume logic, no reinitialization, calendar validation.
- `tests/test_replay.py` — synthetic causality and checkpoint continuity tests.
- `results/2025H1/state.json` — position/rule checkpoint for restart **after the first successful batch**.
- `results/2025H1/summary.json` — cumulative results, partial/final status and true June 30 balance.
- `results/2025H1/batches/YYYY-MM-DD_to_YYYY-MM-DD/`:
  - `rules_1min.csv` — each minute's actual evaluated rule state.
  - `equity_10min.csv`, `rules_10min.csv` — snapshots.
  - `trades.csv` — every execution, fees, actual execution assumptions.
  - `rule_events.csv` — all stop/risk-rule transitions.
  - `daily_equity.csv` and `data_coverage.csv` — daily equity and data integrity.
  - `batch_summary.json` — cumulative batch-to-batch account balance.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/batch_replay.py --batch-start 2025-01-01 --batch-end 2025-01-14 --out results/2025H1
python src/batch_replay.py --batch-start 2025-01-15 --batch-end 2025-01-28 --out results/2025H1
# Continue contiguous 14-calendar-day batches until 2025-06-30.
```

Or run [the GitHub Actions workflow](../../actions/workflows/replay-2025.yml), which executes all batches in chronological order and commits after each successful batch.

## Source, reproducibility and limitations

Actual recorded 1-minute stock bars are downloaded at runtime from [mito0o852/OHLCV-1m](https://huggingface.co/datasets/mito0o852/OHLCV-1m), a third-party US-stock data collection, reportedly originating from Finnhub. Raw data is not republished here. Monthly source files could change, and corporate-action-adjusted prices, missing delisted tickers, incomplete trading universe, and historical ticker renames can introduce **survivorship or ex-post adjustment bias** even in an otherwise causal replay. A 1-minute candle cannot reproduce order-book market impact. Reported virtual P&L is not verified achievable brokerage performance. Snapshot timestamps represent **simulation time**, not backdated Git commits.

If raw data cannot be downloaded, coverage is incomplete, or replay/commit fails, the workflow stops with no fabricated year-end/June-end P&L. Only completed, successfully saved batches are treated as valid.
