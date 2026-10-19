# 2020–2025 S&P 500 large-cap medium-term rules backtest

**Separate six-year experiment** (2020-01-02–2025-12-31), with all older 2024–2025 results retained. Starts with **$100,000**, no leverage, cash earns 0%, and fees/slippage total **6 bp per trade side**. Uses at least 2018-2019 historical data as indicator warm-up.

## Crucial scope limitation

The automatic **proxy** variant uses the **100 S&P 500 constituents with highest average daily dollar trading volume over the previous 63 sessions, as measured on the previous year's last trading day**. This is **not** the exact 100 highest market-cap names. Neither historical news explaining 10% drops nor historical P/E / EV-EBITDA / FCF valuation is verified in proxy mode. It is not the requested *full value-screened top-100* investment strategy. `--mode full` fails without separately sourced and time-stamped historical rank and valuation CSV files. A price-only screen cannot prove a drawdown was "without reason".

## Same entry and risk rules as before

- Daily signal after previous session's close; order at next session's **synthetically total-return-adjusted open**.
- **Sell-off reversal:** five-session return <= -10%, at least 7pp worse than SPY, SPY five-day performance > -4%, opening gap better than -6%; require positive day >=2% off prior 3-session low, RSI(14) <48 and price >90% SMA200.
- **Trend:** price > SMA20 > SMA50 > SMA200, RSI14 48–68 and price within 6% of its 63-session high.
- Trade only active S&P 500 index constituents in that year's predetermined basket, price >$5, 63-session average daily dollar volume >$20m, 63-day annualized volatility <65%.
- Max 10 stocks, max 12% position equity when entered; portfolio 90% invested if SPY above 200-day SMA, otherwise 60%.
- All routes: -8% stop (triggered by close), -12% drawdown from peak close (triggered by close), +20% with RSI>72, index deletion or **first session at/after 4 calendar months** exit. Gaps can cause loss beyond thresholds.
- Two variants held separately:
  - **original:** below 97% of SMA50 AND negative daily return -> exit next open for *both* trend and dip-reversal entries.
  - **route_aware:** same SMA50 exit for trend only; dip-reversal positions exit on +6% gain and SMA20 reclaim. This is a **post-hoc** repair chosen after inspecting 2024–2025 outcomes; do not present the 2020–2025 total as an out-of-sample validation.

## Additional data integrity

Point-in-time S&P constituents and adjusted OHLCV data from [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data) release `data`; exclude known no-trade dates and recycled tickers. The series is adjusted using an ex-post data vintage (2026), so corporate-action revisions may not be strictly point-in-time.

**Unverifiable acquisition payout exception:** when an existing holding is deleted from the S&P 500 universe with no next tradable open, cash is *synthetically settled at the last known adjusted close*, explicitly logged as `SYNTHETIC_SETTLEMENT / UNVERIFIED_CORPORATE_ACTION_PAYOUT`. This avoids carrying stale holdings (prior experiment carried PXD) but is **not executable and not proven identical to actual cash/stock merger consideration**. Result is accounting-proxy P&L; settlement count and details are recorded in summary.json. If such settlements occur, results should not be treated as proven investable execution. No taxes, real broker fills, borrow constraints, or sector exposure constraints modeled.

Full mode CSV inputs:
- `input/top100_pit.csv` fields `year,ticker,rank,asof_date`, 100 rank rows/year for **every year 2020–2025**, dates before corresponding year.
- `input/valuation_pit.csv` fields `ticker,published_at,pe_ttm,ev_ebitda,fcf_yield,net_debt_ebitda,revenue_growth,operating_margin` (as-known with two-day publication delay).
- Even with both, proving a decline had no contemporaneous economic explanation requires a separate point-in-time news/filings feed.

## Execute locally

    python -m pip install -r experiments/medium_term_2020_2025/requirements.txt
    python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode original --out experiments/medium_term_2020_2025/results/original
    python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode route_aware --out experiments/medium_term_2020_2025/results/route_aware

Both versions are executed via `.github/workflows/medium-term-2020-2025.yml`. Workflow asserts **all six years**, 100-stock annual universe, and real daily price history before committing outputs to their own directories. Results contain `summary.json`, `summary.md`, `equity_curve.csv`, `trades.csv`, `monthly.csv`. Versions are held fixed; no retrospective tuning to maximize 2020–2025 performance.
