# 2020–2025 rule-based mid-term trading: entire historical S&P 500

Standalone universe-expansion experiment alongside [the historical top-100 by 63-day dollar-liquidity proxy](../medium_term_2020_2025/). **The only intentional strategy difference is the eligible universe:** screen **every company that belonged to the S&P 500 on the signal date**, not just the top 100 by last-December trading dollars. S&P 500 usually comprises about 500 constituents, and index membership varies throughout the year. Stock/constituent data remain from the same Johnbrick123/sp500-data release.

## Period / capital / execution (unchanged)

- **2020-01-02 through 2025-12-31**, daily signals from the prior close, order execution next morning's synthetic dividend-adjusted open, 2018–19 initialization.
- $100,000 starting equity, no leverage, uninvested cash 0% interest, **6bps commissions + slippage per side**.
- At most **10 holdings**, initial equity weight <=12% for each, cap gross investment at 90% when SPY above its SMA200 / 60% when SPY below.
- Every candidate must have adjusted price >$5; last 63 sessions' average dollar turnover >$20m/day; last 63 sessions' annualized realized volatility <65%.
- Buy via **reversal** only following <=-10% 5-session return and 7pp relative underperformance of SPY, SPY itself >-4%, opening gap >-6%, >=2% rebound from last 3-session low, RSI14 <48, price >90% SMA200. **This does not prove the decline was 'without reason'.**
- Or buy via **trend** when price > SMA20 > SMA50 > SMA200, RSI14 in [48,68], >=94% of 63-day high.
- Exit using prior-close signals and next-open fills: <=-8% vs entry, <=-12% trailing peak-close loss, +20% and RSI>72, SP500 deletion, and **forced sell at first tradable morning at/after 4 calendar months**. Overnight gaps can exceed loss thresholds.
- Test **both identical pre-existing exit variants**: `original` exits both reversal and trend upon SMA50 trend break; `route_aware` exits the trend sleeve on SMA50 break, while reversal sleeve takes +6% if SMA20 is reclaimed. This revision was developed after seeing earlier test data, thus results are **in-sample and NOT a fresh blinded holdout**.
- Candidate selection, scoring, weighting, stop parameters, and execution assumptions are copied from the 100-stock experiment **without performance retuning**. Dynamic point-in-time membership is the sole designed difference.

## Important differences, limitations, and proof

The **S&P 500 universe here does not mean buying all 500 stocks**. Each date, the 500-odd historically active constituent names are scanned; the algorithm then filters signals and buys at most ten qualifying names. This answers the request to expand from 100 to 500 investable candidates, without silently increasing diversification or leverage.

This remains a **price/technical exploratory proxy**, not a value+news investigation. No historical market-cap, historical valuation multiple (P/E/EV/EBITDA/FCF yield), or verified cause-of-crash input is provided. Optional full mode only works with genuinely as-published dated historical `input/valuation_pit.csv`; it still does *not* check why stocks fell.

The upstream dataset is compiled in 2026. It covers point-in-time constituent memberships but can have vendor backfills/corporate-action corrections not available historically. The `recycled_tickers.csv` names are excluded; `no_trade_days.csv` prevents trading recorded nontrade dates. When an existing holding leaves the index and has **no executable next-session open**, the historical code performs a **synthetic non-tradable settlement at its last known adjusted close**, explicitly flagged in `synthetic_settlement_details`. This is *not validated cash/stock deal consideration*; see the raw result before treating P&L as implementable. Other missing data, overnight gaps, spread/slippage changes, taxes, mergers, sector exposure, and portfolio beta limit any investment claim.

## Run

```bash
python -m pip install -r experiments/medium_term_2020_2025_sp500/requirements.txt
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode original --out experiments/medium_term_2020_2025_sp500/results/original
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode route_aware --out experiments/medium_term_2020_2025_sp500/results/route_aware
```

The GitHub Actions workflow `.github/workflows/medium-term-2020-2025-sp500.yml` runs both backtests, verifies **six full calendar years, all 500-ish constituents in prior-December snapshots, no 100-stock cap**, and commits reproducible `summary.md`, `summary.json`, `equity_curve.csv`, `monthly.csv`, `trades.csv` separately per exit variant.

Compare with original 100-candidate results in `../medium_term_2020_2025/results/`. Both are historical simulations, **not** projections.
