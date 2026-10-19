# 2020–2025 six-year execution report

All figures below are computed from two successful GitHub Actions runs over 1,508 daily market sessions; starting NAV USD 100,000. **This is a 100-most-liquid historical constituent price/technical proxy**, NOT the requested historical top-100-market-cap and PIT-value strategy. History retrieved from the [point-in-time constituent/adjusted price dataset](https://github.com/Johnbrick123/sp500-data). No historical multiple/news gates were populated.

## Account returns vs dividend-adjusted SPY

| Year | Original exit, ending NAV | Original annual % | Route-aware annual % | SPY annual % |
|---|---:|---:|---:|---:|
| 2020 | $106,081.35 | +6.081 | +6.858 | +18.373 |
| 2021 | $129,454.28 | +22.033 | +22.033 | +28.744 |
| 2022 | $114,204.17 | -11.780 | -12.390 | -18.172 |
| 2023 | $122,384.61 | +7.163 | +5.116 | +26.189 |
| 2024 | $132,749.48 | +8.469 | +11.257 | +24.885 |
| 2025 | **$124,373.08** | -6.310 | -7.186 | +17.715 |

| Overall 2020–2025 | Original | Route-aware | SPY |
|---|---:|---:|---:|
| Ending account NAV | $124,373.08 | $124,008.34 | n/a |
| Cumulative total return | **+24.373%** | **+24.008%** | **+130.138%** |
| CAGR | +3.705% | +3.654% | n/a |
| Max drawdown | -23.541% | -24.298% | n/a |
| Volatility annualized | 12.409% | 12.513% | n/a |
| Sharpe, zero risk-free | 0.353 | 0.347 | n/a |
| Orders (including proxy settlements) | 690 | 680 | n/a |
| Completed positions | 340 | 335 | n/a |
| Realized win rate | 36.18% | 36.12% | n/a |
| End-of-2025 open holdings | 10 | 10 | n/a |

*The 2024–2025 subperiod rows differ from separate standalone 2024–2025 runs because this simulation **carries capital and positions forward from 2020**. The standalone backtest starts fresh in January 2024 and is a different portfolio path.*

## Entry signal frequency

| Entry reason | Original buys | Route-aware buys |
|---|---:|---:|
| Trend-following | **339** | **335** |
| 10% sell-off followed by proxy rebound | **11** | **10** |
| Total buys | 350 | 345 |

97% of original entry transactions are the *trend* sleeve (339/350). **The result is not evidence that buying cheap shares after an unexplained 10% dip works.** Valuation/news screens absent, and there are too few dip entries for reliable inferential statistics.

## Exit results (original, n=340)

| Trigger | Count | Win rate | Avg realized position return |
|---|---:|---:|---:|
| 50-day trend break | **200** | 17.5% | -3.04% |
| -8% close-based hard-stop | **37** | 0% | -10.30% |
| -12% trailing-close stop | 20 | 25% | -2.72% |
| 20%+ profit and overbought | 41 | 100% | +22.53% |
| Four-month maximum exit | 40 | 100% | +9.64% |
| Historical corporate event synthetic settlement | 2 | 100% | +0.48% |

**Regime weakness:** The strategy lagged SPY in 2020, 2021, 2023, 2024 and 2025, though it had a smaller loss than SPY in 2022. Closing orders after close-based stop signals can still lose much more than 8%; TWTR exit on 2020-11-02 was -20.88%, with IBM, GE and V also at -13% or worse in April 2025.

## Synthetic merger/delisting settlement flags

The source has no fill at the next open after S&P member removal for the following holdings, so *neither* strategy can prove a real disposal price:

- **TIF** 2021-01-07: synthetic last adjusted close **131.46**.
- **PXD** 2024-05-08: synthetic last adjusted close **269.62**.

They were credited at last quoted adjusted close plus modeled fees. This is **not an executable order** or an independently verified merger consideration. The pricing assumption is likely to change actual portfolio results and must be reconciled with original merger documentation/cash-or-stock terms. The report deliberately exposes it rather than silently marking stale shares as permanently held. The original 2024–25 model did carry a stale acquired stock, and this six-year correction is not a fully audited corporate-actions engine.

## Conclusions and next research questions

1. Across these six in-sample years, the fixed **original exit** version modestly beats route-aware (+24.373 vs +24.008), but *both badly lag SPY*. Route-aware was selected after seeing 2024–25, not a blind independent test.
2. The system mostly buys momentum and repeatedly stops trend breaks. Evaluate trend retention/churn and active market exposure, and report sector weights and contribution. **Do not revise parameters to fit 2020–2025 and then report that as OOS edge**.
3. Need the true historical **market-cap-ranked** top 100 (as of each preceding Dec), not liquidity proxy. Dates and historical share counts matter.
4. Need as-known filings/financials with their publish timestamps and contemporaneous negative-news gates. An unexplained drop is **not defined by a return threshold alone**.
5. Reconcile actual acquisition settlements and independent adjusted/opens before asserting executable six-year returns.
6. Run future-style walk-forward on predeclared rules and benchmark against SPY with matched beta, gross exposure and costs.

Reproduce with the root workflow or scripts in this directory; inspect results/original and results/route_aware for summary JSON, trade CSV, monthly returns and daily equity.
