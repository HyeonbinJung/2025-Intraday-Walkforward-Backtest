# Results · 2020–2025 · full historical S&P 500

[← Experiment specification](../README.md) · [← Project results](../../../docs/RESULTS.md)

> [!NOTE]
> These are separate **hypothetical** account replays. The result `COMPLETE` indicates all coded dates were processed, **not** audited real fills. The 100-name basket is the top 100 by historical *dollar-volume*, not market cap. The full-index basket screens historical members but holds at most ten names.

| Exit variant | Simulation status | Ending NAV | Total return | Maximum drawdown |
|:--|:--|--:|--:|--:|
| [Original / v1](original/README.md) | COMPLETE · 1508 sessions | $106,429.99 | +6.43% | -22.20% |
| [Route-aware / v1.1 · post-hoc](route_aware/README.md) | COMPLETE · 1508 sessions | $124,601.04 | +24.60% | -25.08% |

## What the files mean

| Filename | Use |
|:--|:--|
| `README.md` inside each variant | Human-readable scorecard and caveats |
| `summary.json` | Machine-readable source of numerical claims |
| `summary.md` | Historical simulator's auto-generated snapshot |
| `equity_curve.csv` | Full daily account-equity time series |
| `monthly.csv` | Month-end compounded return stream |
| `trades.csv` | Entry/exit ledger, costs, and reason codes |

Human-readable pages are curated for stable navigation. The simulator may overwrite its own `summary.md` if rerun. Read the machine record before editing any reported number.
