# Research results · Verified snapshots

[← Project home](../README.md) · [Experiment catalog](../experiments/README.md) · [Methodology](METHODOLOGY.md)

> [!IMPORTANT]
> **All figures are virtual backtest outputs, not realized brokerage performance.** A run marked `COMPLETE` has finished its coded date range; this does **not** mean historical economic assumptions or executable fills are independently audited.

## 01 / Intraday: one-minute replay

| Variant | Window | Completion | Initial NAV | Last reported NAV | Period return |
|:--|:--|:--|--:|--:|--:|
| **I-01 / Original** | 2025-01-01 → 2025-06-30 | **COMPLETE** · 122/122 sessions | $100,000.00 | **$40,809.57** | **-59.19%** |
| **I-02 / Low-turnover v2** | 2025-01-01 → 2025-06-30 *requested* | **PARTIAL** · 8/122 sessions | $100,000.00 | $97,551.06 **checkpoint only** | **not reported** |

Original simulation: 31,241 fills, 47,580 minute rule checks, modeled trading costs of **$48,052.35**. The v2 snapshot includes 705 fills, 3,120 rule checks, modeled costs of **$1,468.88** for the **eight completed sessions**. These are not comparable full-period P&L observations. Do **not** describe $97,551.06 as v2's June 30 ending NAV.

[Original full report](../results/2025H1/README.md) · [v2 partial checkpoint](../results/2025H1_v2/README.md) · [Original failure analysis](../results/2025H1/POSTMORTEM_AND_V2_PROMPT.md)

## 02 / Medium term: 2024–2025 · 100 liquid constituents

**Standalone two-year portfolios**. $100,000 initial capital each, 502 sessions, two exit schemes, six basis points modeled **per side**.

| Measure | S-01 / Original exits | S-01 / Route-aware exits | SPY matched period |
|:--|--:|--:|--:|
| End NAV | **$117,476.38** | **$117,083.67** | — |
| Cumulative return | +17.48% | +17.08% | **+47.99%** |
| CAGR | +8.40% | +8.22% | — |
| Maximum drawdown | -14.19% | -14.71% | — |
| Realized win rate | 37.50% | 38.00% | — |
| Closed positions | 104 | 100 | — |
| Open positions at last mark | 10 | 10 | — |

[Experiment specification](../experiments/medium_term_2024_2025/README.md) · [Original results](../experiments/medium_term_2024_2025/results/proxy/README.md) · [Revised results](../experiments/medium_term_2024_2025/results/proxy_route_aware/README.md)

## 03 / Medium term: 2020–2025 · 100 liquid vs all index members

**Continuous six-year portfolios**, starting in 2020 with $100,000; *not* independently reset in 2024. The original rule applies the 50-day trend break to both entry types; route-aware differentiates the two. Both are **in-sample simulations**; the route-aware change was informed by prior 2024–2025 diagnostics.

| Measure | 100 liquid / original | 100 liquid / route-aware | All S&P 500 / original | All S&P 500 / route-aware |
|:--|--:|--:|--:|--:|
| End NAV | $124,373.08 | $124,008.34 | $106,429.99 | **$124,601.04** |
| Total return | +24.37% | +24.01% | +6.43% | +24.60% |
| CAGR | +3.71% | +3.65% | +1.05% | +3.74% |
| Maximum drawdown | -23.54% | -24.30% | -22.20% | -25.08% |
| Annualized volatility | 12.41% | 12.51% | 11.94% | 12.08% |
| Sharpe (0% risk-free) | 0.353 | 0.347 | 0.153 | 0.370 |
| Realized win rate | 36.18% | 36.12% | 37.82% | 41.82% |
| Completed trades | 340 | 335 | 349 | 330 |
| Synthetic non-executable exits | **2** | **2** | **8** | **8** |

The dividend-adjusted **SPY buy-and-hold benchmark returned +130.14%** across this same six-year window. All four modeled strategies lagged the benchmark by more than 100 percentage points. Wider universe scanning improved the *number of observed dip signals*, but did not produce market-beating performance.

### Annual returns · same six-year account histories

| Year | 100 / Original | 100 / Route-aware | S&P 500 / Original | S&P 500 / Route-aware | SPY |
|:--|--:|--:|--:|--:|--:|
| 2020 | +6.08% | +6.86% | -11.78% | +2.83% | +18.37% |
| 2021 | +22.03% | +22.03% | +20.54% | +20.55% | +28.74% |
| 2022 | -11.78% | -12.39% | -3.40% | -6.62% | -18.17% |
| 2023 | +7.16% | +5.12% | -6.80% | -8.63% | +26.19% |
| 2024 | +8.47% | +11.26% | +11.74% | +18.46% | +24.89% |
| 2025 | -6.31% | -7.19% | -0.51% | -0.55% | +17.72% |

[100-stock experiment](../experiments/medium_term_2020_2025/README.md) · [Entire S&P 500 experiment](../experiments/medium_term_2020_2025_sp500/README.md) · [Direct comparison / exit analysis](../experiments/medium_term_2020_2025_sp500/RESULTS_COMPARISON.md)

## 04 / Sequential 2018–June 2026 swing · adaptive six-month exit

**Continuous $100,000 portfolio: 2018 model development, 2019H1 first forward-selected policy, 2019H2 review, 2020–2025 yearly policy reviews, 2026H1 liquidation only.** Historically active S&P 500 constituents, price-only technical signals and 6 bp per side.

> [!CAUTION]
> **COMPLETE PROXY, NOT A VERIFIED FUNDAMENTAL STRATEGY.** Historical financial valuation, direct competitor inputs, and verified absence of material adverse news are not available in the committed datasets. Five non-tradable events are booked as zero-recovery **non-executable** write-offs (roughly $37,079.68 of entry capital); true merger/corporate-action proceeds are unknown. 2018–2025 was already historical when the model family was designed.

| Measure | S-04 sequential simulation | Matched SPY buy-and-hold |
|:--|--:|--:|
| Tested window | 2018-01-02 → 2026-06-30 | Same years |
| Initial capital | $100,000.00 | Illustrative $100,000 |
| Ending NAV | **$99,216.93** | Approx. $318,979 before benchmark trading costs |
| Total return | **-0.78%** | **+218.98%** |
| Maximum drawdown | -27.86% | Not calculated here |
| Executed sales | 301 | — |
| Realized win rate on executed sells | 52.82% | — |
| Synthetic or assumed ordinary merger sales | **0** | — |
| Non-executable zero-recovery write-offs | **5** | — |
| 2026 purchases / positions at end | **0 / 0** | — |

Annual S-04 NAV and return are on the **same continuous portfolio**, not separately restarted accounts:

| Year | S-04 return | SPY return |
|:--|--:|--:|
| 2018 · development | +6.77% | -4.56% |
| 2019 · 1H/H2 sequential selection | -12.04% | +31.22% |
| 2020 | +5.05% | +18.37% |
| 2021 | -1.97% | +28.74% |
| 2022 | -0.93% | -18.17% |
| 2023 | +3.59% | +26.19% |
| 2024 | +4.11% | +24.89% |
| 2025 | -9.04% | +17.72% |
| 2026H1 · liquidation only | +5.57% | +10.09% |

For **2019H1** alone, account return was **-3.52%**; **2019H2 -8.83%**. The **2020–2025 continuing account segment** returned approximately **+0.07%** (not a fresh $100,000 account). 2026's last recorded simulated SELL is February 17, after which the balance remained cash through June 30.

![S-04 and SPY annual historical NAV comparison](../experiments/medium_term_2018_2026_walkforward/results/performance.svg)

[Complete S-04 report](../experiments/medium_term_2018_2026_walkforward/results/README.md) · [Source code](../experiments/medium_term_2018_2026_walkforward/backtest.py) · [Machine summary](../experiments/medium_term_2018_2026_walkforward/results/proxy/summary.json) · [Dated policy switches](../experiments/medium_term_2018_2026_walkforward/results/proxy/policy_log.json)

## Evidence trail

| What to inspect | Canonical path |
|:--|:--|
| Intraday original machine summary | [results/2025H1/summary.json](../results/2025H1/summary.json) |
| Intraday v2 **partial** machine summary | [results/2025H1_v2/summary.json](../results/2025H1_v2/summary.json) |
| S-01 original | [2024–25 / proxy / summary.json](../experiments/medium_term_2024_2025/results/proxy/summary.json) |
| S-01 route-aware | [2024–25 / proxy_route_aware / summary.json](../experiments/medium_term_2024_2025/results/proxy_route_aware/summary.json) |
| S-02 original | [2020–25 / original / summary.json](../experiments/medium_term_2020_2025/results/original/summary.json) |
| S-02 route-aware | [2020–25 / route_aware / summary.json](../experiments/medium_term_2020_2025/results/route_aware/summary.json) |
| S-03 original | [Full index / original / summary.json](../experiments/medium_term_2020_2025_sp500/results/original/summary.json) |
| S-03 route-aware | [Full index / route_aware / summary.json](../experiments/medium_term_2020_2025_sp500/results/route_aware/summary.json) |
| S-04 sequential 2018–2026 | [Sequential simulation / proxy / summary.json](../experiments/medium_term_2018_2026_walkforward/results/proxy/summary.json) |

## Interpretation boundaries

- **100-stock** means top 100 by *prior 63-session dollar trading volume as ranked at the preceding year-end* among historical S&P 500 members, **not** top 100 by capitalization.
- **Full S&P 500** scans all historically active member tickers (roughly 503–508), but buys **no more than 10 positions at a time**.
- A fully validated value strategy requires timestamped P/E, EV/EBITDA, cash-flow metrics and contemporaneous event/news; these were not used in the automatic daily runs.
- Two or eight historical acquisition exits per six-year variant use **synthetic last-close settlement assumptions**, not verified actual cash/stock proceeds. Those results are not necessarily reproducible real transactions.
- Results of separate windows start from different portfolio histories. Six-year portfolio 2024/25 segment ≠ two-year standalone 2024/25 backtest.
- This page reproduces stored experiment data; no optimization, additional trading, or backtest re-execution is implied by this editorial summary.

Further limitations: [Data integrity, risk and what is not verified](DATA_QUALITY.md).
