# I-01 · Monthly equity and drawdown report

[← Intraday baseline](README.md) · [Project results](../../docs/RESULTS.md) · [Failure analysis](POSTMORTEM_AND_V2_PROMPT.md)

> [!IMPORTANT]
> **COMPLETE:** 2025-01-01 → 2025-06-30, **122 NYSE sessions**, starting from **$100,000.00**. Simulated end balance **$40,809.57 (-59.19%)**. These are a synthetic historical account and not real broker fills.

## Account trajectory · six month-ends

| Period | Start equity | End equity | Dollar P&L | Month return | Cumulative return |
|:--|--:|--:|--:|--:|--:|
| **Jan 2025** | $100,000.00 | $84,128.81 | -$15,871.19 | -15.87% | -15.87% |
| **Feb 2025** | $84,128.81 | $72,644.46 | -$11,484.35 | -13.65% | -27.36% |
| **Mar 2025** | $72,644.46 | $60,018.22 | -$12,626.24 | -17.38% | -39.98% |
| **Apr 2025** | $60,018.22 | $50,804.77 | -$9,213.45 | -15.35% | -49.20% |
| **May 2025** | $50,804.77 | $46,388.53 | -$4,416.24 | -8.69% | -53.61% |
| **Jun 2025** | $46,388.53 | **$40,809.57** | -$5,578.96 | -12.03% | **-59.19%** |

## Snapshot and execution accounting

| Measure | Value |
|:--|--:|
| Opening NAV | $100,000.00 |
| Closing NAV | **$40,809.57** |
| Total hypothetical P&L | **-$59,190.43** |
| Total return | **-59.19%** |
| Completed historical batches | 13 |
| Minutes with risk evaluation | 47,580 |
| Fill records | 31,241 |
| Modeled cumulative trading costs | $48,052.35 |

The source's monthly values are reconstructed from the **last NYSE session's end-of-day account equity** in each committed batch, with no additional deposits or withdrawals. January starts at $100,000; later monthly returns use the preceding month's close and **compound**, rather than being arithmetically summed.

## Provenance and limitations

- [Machine summary](summary.json) is the source for completion, account value and cost estimates.
- [Month-end CSV](monthly_equity.csv) is the machine-readable companion.
- [Per-batch daily equity / trades / coverage](batches/) can be used to audit how each monthly row was reconstructed.
- Bar-level historical input may contain survivorship and after-the-fact corporate-action information. Estimated next-minute fills and fixed execution costs cannot replicate order-book reality.

[Read why this experiment failed →](POSTMORTEM_AND_V2_PROMPT.md)
