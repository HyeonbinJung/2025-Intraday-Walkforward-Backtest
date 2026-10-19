# I-01 · 2025H1 intraday baseline · completed

[← Intraday results](../README.md) · [Experiment catalog](../../experiments/README.md) · [All returns](../../docs/RESULTS.md)

> [!IMPORTANT]
> **COMPLETE / 122 of 122 NYSE sessions (2025-01-01 through 2025-06-30).** This is a *loss-making historical replay*, not a live account or successfully validated trading edge.

## Key results

| Metric | Committed value |
|:--|--:|
| Starting account | $100,000.00 |
| Ending account | **$40,809.57** |
| Net change | **-$59,190.43** |
| Full-period return | **-59.19%** |
| Minute-by-minute rule checks | 47,580 |
| Fill records | 31,241 |
| Historical batches | 13 |
| Estimated transaction costs | **$48,052.35** |
| Covered / expected sessions | 122 / 122 |

## Monthly account trajectory

| Month-end | Ending equity | Return during month | Return since inception |
|:--|--:|--:|--:|
| Jan 2025 | $84,128.81 | -15.87% | -15.87% |
| Feb 2025 | $72,644.46 | -13.65% | -27.36% |
| Mar 2025 | $60,018.22 | -17.38% | -39.98% |
| Apr 2025 | $50,804.77 | -15.35% | -49.20% |
| May 2025 | $46,388.53 | -8.69% | -53.61% |
| Jun 2025 | **$40,809.57** | -12.03% | **-59.19%** |

## Primary failure modes

The previous investigation attributes the loss in part to **excessive turnover and significant modeled execution costs**. Market-impact realism, entry threshold and adaptation quality warrant additional evaluation; correlation with cost drag alone does not prove a fully cost-free counterfactual would have succeeded.

[Full failure analysis](POSTMORTEM_AND_V2_PROMPT.md) · [Detailed monthly calculations](MONTHLY_REPORT.md)

## Data and proof

| File | Purpose |
|:--|:--|
| [summary.json](summary.json) | Canonical state, full-period completion flag and aggregate P&L |
| [monthly_equity.csv](monthly_equity.csv) | Reconstructed committed month-end values |
| [state.json](state.json) | Historical end-of-run account and rule checkpoint |
| [batches/](batches/) | Per-batch minute decisions, trades, bar coverage, risk events and daily equity |
| [source code](../../src/backtest.py) | Simulator rules |
| [batch manager](../../src/batch_replay.py) | Historical continuation and state checkpointing |

The bar provider and adjusted historical symbols may introduce survivorship/corporate-action bias. Trades filled using **next minute open assumptions**, fixed slippage and commission, not live market execution. Read [limitations](../../docs/DATA_QUALITY.md).
