# Actual 2020–2025 backtest: ALL historical S&P 500 companies vs 100-stock liquidity-screen proxy

Two historical, unlevered daily simulations each have **1,508 actual sessions** and starting NAV **USD 100,000**. **The only intended rule change between experiments is the stock universe**: prior-year top 100 by dollar volume versus all date-specific S&P 500 membership (between 503 and 508 symbol labels in the dataset). Both portfolios actually own <=10 stocks and enter/exit based on previous closes followed by next opens. 6bp costs per side, 0% idle-cash interest; maximum four months per position. Each version has its original and route-aware exit strategy.

## 6-year performance comparison

| Metric | 100 candidate / original | All S&P 500 / original | 100 candidate / route-aware | All S&P 500 / route-aware |
|---|---:|---:|---:|---:|
| Final NAV | $124,373.08 | **$106,429.99** | $124,008.34 | **$124,601.04** |
| 6yr cumulative return | +24.373% | **+6.430%** | +24.008% | **+24.601%** |
| CAGR | +3.705% | +1.045% | +3.654% | +3.736% |
| Worst peak-to-trough drawdown | -23.541% | -22.196% | -24.298% | -25.083% |
| Annualized volatility | 12.409% | 11.939% | 12.513% | 12.079% |
| Sharpe assuming 0 risk-free | 0.353 | 0.153 | 0.347 | 0.370 |
| Round trips | 340 | 349 | 335 | 330 |
| Realized win rate | 36.18% | 37.82% | 36.12% | 41.82% |
| Synthetic deal-price settlements | 2 | **8** | 2 | **8** |

Matched SPY buy-and-hold cumulative return: **+130.138%**. The full-500 original result is **-123.708 percentage points** short of SPY, while the route-aware result is **-105.537 percentage points** short. Both underperform considerably even before independent reconciliation of corporate actions.

Relative to their respective 100-stock variants:
- Full-500 **original** worsens cumulative return by **17.943 percentage points**.
- Full-500 **route-aware** improves cumulative return by only **0.593 percentage points** while its MDD worsens by 0.785pp. These are same-history results, **not a statistically independent discovered alpha**.

## Yearly returns (percentage)

| Year | 100 / original | All 500 / original | 100 / route-aware | All 500 / route-aware | SPY |
|---|---:|---:|---:|---:|---:|
| 2020 | +6.081 | **-11.781** | +6.858 | **+2.830** | +18.373 |
| 2021 | +22.033 | **+20.541** | +22.033 | **+20.553** | +28.744 |
| 2022 | -11.780 | **-3.402** | -12.390 | **-6.622** | -18.172 |
| 2023 | +7.163 | **-6.801** | +5.116 | **-8.629** | +26.189 |
| 2024 | +8.469 | **+11.736** | +11.257 | **+18.464** | +24.885 |
| 2025 | -6.310 | **-0.507** | -7.186 | **-0.554** | +17.715 |

## Entry and exit diagnostics

| Measure | 100 / original | 500 / original | 100 / route-aware | 500 / route-aware |
|---|---:|---:|---:|---:|
| Buy transactions | 350 | 359 | 345 | 340 |
| Trend entries | 339 | 328 | 335 | 312 |
| Dip-reversal entries | 11 | **31** | 10 | **28** |
| Trend-break exits | 200 | 241 | 186 | 193 |
| Close-based -8% stop exits | 37 | 22 | 45 | 34 |
| Dip recovered exit | N/A | N/A | 6 | **18** |
| Missing merger-consideration settlements | 2 | **8** | 2 | **8** |

The larger universe captures nearly three times as many dip-reversal signals (11 -> 31 original, 10 -> 28 route-aware), but **even 31 observations is a weak basis for estimating a genuine dip-reversal edge**. 500/original has 241 exits after breaking the 50-day trend, versus 200 under 100/original. The route-aware rules improve the outcomes of 500-stock version compared with its original version, but those route-aware rules were selected **after looking at 2024–25**.

## Corporate action reconciliation required

Both all-500 variants synthetically close the following **8** holdings at last adjusted close, because a verified, tradable next open is not available; **these are assumptions rather than real executable fill prices or audited merger consideration:**

- TIF (2021-01-07) 131.46
- VAR (2021-04-20) 177.07
- FLIR (2021-05-14) 57.34
- ALXN (2021-07-21) 182.50
- CERN (2022-06-08) 94.92
- CTXS (2022-10-03) 103.90
- WBA (2025-08-28) 11.98
- K (2025-12-11) 83.44

Last adjusted closes here are numerical portfolio bookkeeping in adjusted synthetic shares, not necessarily raw market price dollars or settlement proceeds. A real company merger may involve stock conversion, cash, or fractional shares. Backtesting must reconcile this independently; **do not treat these outputs as fully implementable performance**.

## Limits and next decisions

- Price/technicals only: **there is no as-filed valuation P/E, EV/EBITDA, FCF yield, audited negative-news filter, or proven unexplained >=10% drop**. The full index is truly screened each session, but the genuine fundamental-strategy performance **has not been measured**.
- This data series is rebuilt after the trading periods (2026 vintage), so its corporate-action history may be retrospectively corrected. Current data does include historic S&P 500 membership to avoid *today's 500 survivors only* bias.
- The **10 holding cap** remains identical; 500-stock screening does not mean equally owning all 500 or being fully invested all the time.
- Original/route-aware were already designed in prior 2024–25 work. 2020–25 includes inspected years; therefore these returns do not validate out-of-sample forecasting skill.
- Increasing candidates alone neither guaranteed nor delivered SPY outperformance. Before further parameter tuning, reconcile the 8 settlement records, report sector allocations and realized exposure, and implement audited historical valuation and event screening.

## Files

- [Full-index original results](results/original/summary.md) and [trades](results/original/trades.csv)
- [Full-index route-aware results](results/route_aware/summary.md) and [trades](results/route_aware/trades.csv)
- [100-candidate benchmark results](../medium_term_2020_2025/RESULTS_ANALYSIS.md)
- Workflow: [2020-2025-sp500](../../.github/workflows/medium-term-2020-2025-sp500.yml)
