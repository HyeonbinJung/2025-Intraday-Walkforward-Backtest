# Experiment catalog

[← Project home](../README.md) · [All results](../docs/RESULTS.md) · [Methods](../docs/METHODOLOGY.md)

## Intraday research

| ID | Experiment | State | Inputs | Results |
|:--|:--|:--|:--|:--|
| **I-01** | [2025H1 one-minute baseline](../src/) | **Complete** · 122 sessions | 1-minute OHLCV | [Performance & postmortem](../results/2025H1/README.md) |
| **I-02** | [2025H1 lower-turnover v2](../docs/INTRADAY_V2.md) | **Partial** · 8 / 122 sessions | 1-minute OHLCV | [Checkpoint](../results/2025H1_v2/README.md) |

## Medium-term research

| ID | Experiment | Universe | Window | Result snapshots |
|:--|:--|:--|:--|:--|
| **S-01** | [2024–2025 baseline + exit revision](medium_term_2024_2025/README.md) | Prior-year **100 most liquid** members | 502 sessions | [Original](medium_term_2024_2025/results/proxy/README.md) / [Revised](medium_term_2024_2025/results/proxy_route_aware/README.md) |
| **S-02** | [2020–2025 six-year extension](medium_term_2020_2025/README.md) | Prior-year **100 most liquid** members | 1,508 sessions | [Original](medium_term_2020_2025/results/original/README.md) / [Route-aware](medium_term_2020_2025/results/route_aware/README.md) |
| **S-03** | [2020–2025 full-index expansion](medium_term_2020_2025_sp500/README.md) | **All contemporaneous** S&P 500 members | 1,508 sessions | [Original](medium_term_2020_2025_sp500/results/original/README.md) / [Route-aware](medium_term_2020_2025_sp500/results/route_aware/README.md) |

| **S-04** | [2018–2026 adaptive six-month swing / liquidation](medium_term_2018_2026_walkforward/README.md) | All **contemporaneous** S&P 500 members | 2018 development → 2019H1 sequential → 2020–25 yearly → June 2026 exit | [**COMPLETE proxy**, 5 unverified write-offs](medium_term_2018_2026_walkforward/results/README.md) |

### Naming conventions

- `I-` = intraday minute replay; `S-` = medium-term, daily price signals.
- `original` = same 50-day moving-average trend-break exit for trend and reversal entries.
- `route_aware` = differing exit logic for reversal entries; a **post-hoc** rule change.
- `proxy` = the **price-only** strategy, not the complete dated valuation/news strategy.
- `COMPLETE` = the specified historical window finished; **not** verified live execution or statistically demonstrated alpha.

Original result data and source code are preserved. Do not compare `2024–2025` newly initialized accounts with the `2020–2025` account's 2024–2025 segment without noting different initial positions/capital.
