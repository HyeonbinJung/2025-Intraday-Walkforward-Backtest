# 2025 One-Minute Intraday Walk-Forward Backtest

**Initial virtual capital: $100,000**. Replay window: **Jan 1–Dec 31, 2025**. Long-only US equities, up to 5 dynamic momentum/relative-volume candidates.

## Run status

**Results are unverified until results/2025/summary.json says COMPLETE.** Do not substitute a hypothetical return for actual computed results.

See the GitHub Actions tab for **2025 one-minute historical replay**. A push to src/backtest.py triggers the historical run. If it fails, inspect the attached log artifact. You can trigger it again via workflow_dispatch.

## Causal execution model

- NYSE session calendar, holidays and shortened sessions respected; source bars restricted to regular market hours.
- Signal from a fully finished 1-minute bar cannot fill until the next minute's open. No future gain or future volatility is used for picking the five stocks.
- Momentum (5/20 minutes), recent volatility and relative trading volume screen candidates at each minute.
- Every minute evaluates orders, trailing stops and risk rules; every realized losing position exit tightens momentum threshold and reduces allocation (without peeking into what will happen next).
- Each trade has next-bar-open price plus **5 bp estimated adverse slippage per side**, **$0.005 per share commission**, a maximum participation of **1% of minute bar volume**.
- Portfolio + rule snapshots every 10 minutes; every fill and loss-rule transition logged individually; equity and trade counts saved for every real NYSE session.
- No fake fills for missing minute candles. If last-minute exits are unfilled, positions remain on the balance sheet, showing overnight exposure rather than inventing executions.

## Data provenance

Source: https://huggingface.co/datasets/mito0o852/OHLCV-1m. Monthly Parquet files for 2025, described by publisher as originally sourced from Finnhub. Data is downloaded to the ephemeral workflow runner; NOT committed. Check licensing before redistribution.

Limitations: source universe may not faithfully contain all delisted IPO/meme/low-liquidity stocks; pre-2025/split adjustments may embed hindsight corporate actions; 1-minute bar open + fixed slippage does not guarantee actual fill; and 1% printed-volume cap does not model market impact completely. Thus this is a historical research simulation, not a genuine real-time strategy track record. Selection is top five **within observed dataset candidates**, NOT independently verified as the entire national market's five biggest gainers.

## Local execution

Install dependencies from requirements.txt, then run:

    python src/backtest.py --out results/2025

Or provide downloaded 2025 monthly Parquet files with --local-dir PATH. Never start with less than the complete 12 months if claiming full-year final performance.

## Outputs

- results/2025/summary.json — completion flag, final equity, net return, costs, trades, drawdown.
- results/2025/daily_equity.csv — daily account balances and realized activity.
- results/2025/equity_10min.csv — 10-minute equity, cash and position snapshots.
- results/2025/trades.csv — each simulated buy/sell fill.
- results/2025/rules_10min.csv — 10-minute active rule state.
- results/2025/rule_events.csv — each risk-rule change, its time and trigger.
- results/2025/data_coverage.csv — minutes/bar count per trading day.

Historical timestamps are embedded in records, not falsified as earlier GitHub commit dates.
