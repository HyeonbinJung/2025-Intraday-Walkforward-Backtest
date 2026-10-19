# Results · 2020–2025 · historical liquidity top 100

[← Experiment specification](../README.md) · [← Project results](../../../docs/RESULTS.md)

> [!NOTE]
> These are separate **hypothetical** account replays. The result `COMPLETE` indicates all coded dates were processed, **not** audited real fills. The 100-name basket is the top 100 by historical *dollar-volume*, not market cap. The full-index basket screens historical members but holds at most ten names.

| Exit variant | Simulation status | Ending NAV | Total return | Maximum drawdown |
|:--|:--|--:|--:|--:|
| [Original / v1](original/README.md) | COMPLETE · 1508 sessions | $124,373.08 | +24.37% | -23.54% |
| [Route-aware / v1.1 · post-hoc](route_aware/README.md) | COMPLETE · 1508 sessions | $124,008.34 | +24.01% | -24.30% |

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
