# Diagnostic review: 2024-2025 historical price-proxy run

**Verified from a completed GitHub Actions run.** This is **NOT** the fully specified S&P 500 historical market-cap top-100 / point-in-time valuation / verified-no-news test. It uses the rolling-dollar-volume top-100 approximation from the preceding year. Do not present its returns as value-strategy evidence.

## Portfolio and benchmark

| Metric | Price-proxy strategy |
|---|---:|
| Opening capital | $100,000.00 |
| Closing marked NAV | $117,476.38 |
| 2024 return | +19.805% |
| 2025 return | -1.944% |
| Full-window return | +17.476% |
| SPY buy-and-hold full-window | +47.990% |
| Cumulative relative underperformance | -30.513 percentage points |
| CAGR | +8.404% |
| Maximum drawdown | -14.193% |
| Annualized volatility | 9.980% |
| 0% risk-free Sharpe | 0.860 |
| Orders (buys plus sells) | 218 |
| Realized completed trades | 104 |
| Realized win rate | 37.50% |
| Marked positions still open at the end | 10 |

## Entry-route audit

| Route | 2024 buys | 2025 buys | Total |
|---|---:|---:|---:|
| Confirmed technical trend | 53 | 53 | **106** |
| 5-day >=10% market-relative dip + reversal proxy | 1 | 7 | **8** |
| All entries | 54 | 60 | **114** |

**93% of entries came from trend-following, not the requested selloff-reversal pattern.** Most of the measured performance comes from the technical-trend branch; do not attribute it to 'unexplained 10% declines' or cheap multiples.

## Exit diagnosis (104 round trips)

| Exit trigger | Count | Hit rate | Mean realized return |
|---|---:|---:|---:|
| Confirmed trend broken | 64 | 23.44% | -2.23% |
| 8% stop trigger, next-open execution | 15 | 0.00% | -10.70% |
| >20% winner with overbought RSI | 14 | 100.00% | +21.19% |
| Reached four-calendar-month horizon | 9 | 100.00% | +9.42% |
| 12% trailing close trigger | 2 | 50.00% | -0.72% |

Average realized winner **+11.59%**, average realized loser **-5.77%**. In 2024: 22 of 44 completed exits profitable (50.0%); in 2025: 17 of 60 (28.3%). These are descriptive observations, **not causal attributions**.

## Largest realized stop losses

| Exit date | Symbol | Return |
|---|---|---:|
| 2025-04-07 | IBM | -16.28% |
| 2025-04-04 | GE | -14.85% |
| 2025-04-07 | V | -13.49% |
| 2025-02-05 | PYPL | -12.97% |
| 2025-02-18 | LULU | -12.20% |
| 2025-04-07 | CVX | -11.53% |

The April 2025 cluster coincided with broad market turbulence surrounding US tariffs: S&P DJI April commentary documents that the S&P 500 briefly breached an intraday 20% drawdown on April 7. This is an *example of why the system cannot call declines 'without a reason' based only on price* and why next-open stops cannot guarantee an 8% executed loss. Source: https://www.spglobal.com/spdji/en/documents/commentary/market-attributes-us-equities-202504.pdf

## Priorities before treating this as an investable value strategy

1. Replace price-dollar-volume proxy with dated market-cap top 100 lists for December 2023 and December 2024. Backtest the actual user-requested universe.
2. Build as-filed historic EPS, EV/EBITDA and FCF yield point-in-time observations; prevent retroactive financial values, require sector-aware valuation thresholds.
3. Introduce a contemporary event-news and earnings gate, and **mark UNKNOWN as unverified**, rather than asserting lack of adverse information.
4. Diagnose trend-broken (64) and gap-stop (15) exits using entry cohort and macro regime before revising thresholds. Avoid optimization on the same two years; any new rule version needs a prior training period and held-out test.
5. Add sector exposure constraints, sector vs index relative strength, overnight gap risk and slippage stress tests at 6/12/25 bps per side.
6. Run *three separately labeled sleeves*: dips-only; valuation+trend; technical-trend-only, plus a benchmark. Do not collapse their apparent edge into one score.

## Reproduction

Run the workflow in the parent repo, or install requirements and run Python in proxy mode. Reproducible raw trades, daily equity and monthly returns are stored in results/proxy; this document summarizes the executed first-pass experiment only.
