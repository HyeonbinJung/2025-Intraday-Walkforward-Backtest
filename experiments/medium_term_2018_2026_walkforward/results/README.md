# S-04 Results · 2018–June 2026 sequential swing simulation

[← Experiment and rules](../README.md) · [← Experiment catalog](../../README.md) · [Data-quality limitations](../../../docs/DATA_QUALITY.md)

> [!CAUTION]
> **COMPLETE PRICE-ONLY PROXY WITH FIVE NON-EXECUTABLE ZERO-RECOVERY WRITE-OFFS.** This does **not** validate point-in-time company fundamentals, direct competitors, negative-news absence or merger consideration. The strategy family itself was created after these historical years, so the sequential policy implementation is **not independently prospective**.

## Status / Snapshot

| Property | Simulation record |
|:--|:--|
| Status | **COMPLETE_PROXY_WITH_UNVERIFIED_WRITEOFFS** |
| Market data | Historical S&P 500 membership and retrospectively adjusted OHLCV |
| Date range | 2018-01-02 → 2026-06-30 |
| Entry cutoff | 2025-12-31 |
| Starting NAV | $100,000.00 |
| Trading cadence | Prior-session close signals → next-session open |
| 2026 status | Liquidation only, **no buys**; terminal cash equals terminal NAV |
| Fundamental / adverse-news candidate reviews | **0** (not checked by PROXY) |

![Annual NAV comparison, S-04 and SPY](performance.svg)

## Headline metrics

| Metric | Simulated strategy | Matched SPY |
|:--|--:|--:|
| Total return | **-0.78%** | **+218.98%** |
| Final NAV on 2026-06-30 | **$99,216.93** | Not same capital/exposure policy |
| Max drawdown | **-27.86%** | Not computed here |
| Sharpe (0% risk-free) | 0.055 | Not computed here |
| Gross invested share, average through 2025 | Approx. **44.25%** | Buy-and-hold |
| Modelled fees | $3,266.69 | Not cost-adjusted |
| Remaining positions | **0** | — |

**Result:** the six-month, +10%-target adaptive proxy did **not** beat SPY. The comparison is not exposure-matched: the strategy averaged around **44%** invested capital; SPY was continuously invested. Five $0 write-offs total approximately **$37,079.68 in entry capital**, with **unknown true liquidation proceeds**. Do not equate the reported return with audited historical attainable wealth.

## Period breakdown

Annual figures below are **one continuous account**, not independent $100,000 yearly restarts.

| Calendar window | Opening NAV | Closing NAV | Strategy return | SPY return | Sessions |
|:--|--:|--:|--:|--:|--:|
| 2018 | $100,000.00 | $106,767.25 | +6.77% | -4.56% | 251 |
| 2019 | $106,767.25 | $93,911.97 | -12.04% | +31.22% | 252 |
| 2020 | $93,911.97 | $98,650.15 | +5.04% | +18.37% | 253 |
| 2021 | $98,650.15 | $96,704.70 | -1.97% | +28.74% | 252 |
| 2022 | $96,704.70 | $95,806.99 | -0.93% | -18.17% | 251 |
| 2023 | $95,806.99 | $99,248.02 | +3.59% | +26.19% | 250 |
| 2024 | $99,248.02 | $103,325.14 | +4.11% | +24.89% | 252 |
| 2025 | $103,325.14 | $93,979.95 | -9.04% | +17.71% | 250 |
| 2026 H1 | $93,979.95 | $99,216.93 | +5.57% | +10.09% | 123 |

**2019 policy-boundary diagnostic:** first half -3.52% (NAV $106,767.25 → $103,007.60), second half -8.83% (NAV $103,007.60 → $93,911.97). Profile selection in 2019H1 only considered prior-2019 shadow returns; 2019H2 used observations through 2019-06-28, never later. **2020–2025 continuous segment:** opening NAV $93,911.97 → $93,979.95 (**+0.07%**); this is not a standalone $100,000 2020 reset. **2026H1:** +5.57% on legacy positions while new buys were blocked.

### Rule-change audit trail

| Profile effective date | Training information through | Selected profile | Selection |
|:--|:--|:--|:--|
| 2018-01-02 | 2017-12-29 | balanced | Fixed initial profile |
| 2019-01-02 | 2018-12-31 | balanced | Prior 252 sessions only |
| 2019-07-01 | 2019-06-28 | reversal_bias | Prior 252 sessions only |
| 2020-01-02 | 2019-12-31 | reversal_bias | Prior 252 sessions only |
| 2021-01-04 | 2020-12-31 | defensive | Prior 252 sessions only |
| 2022-01-03 | 2021-12-31 | reversal_bias | Prior 252 sessions only |
| 2023-01-03 | 2022-12-30 | reversal_bias | Prior 252 sessions only |
| 2024-01-02 | 2023-12-29 | reversal_bias | Prior 252 sessions only |
| 2025-01-02 | 2024-12-31 | reversal_bias | Prior 252 sessions only |

These are deterministic pre-scheduled selection points. Four fixed historical shadow strategies are compared on trailing equity history; the highest historical risk-adjusted score is used only for future entries.

## Trade diagnostics

| Diagnostic | Count or value |
|:--|--:|
| New buys, 2018–2025 | **306** |
| Executed simulated sells | **301** |
| Executed-sell win rate | **52.82%** |
| +10% target triggered exits | 152 |
| -8% entry loss triggered exits | 114 |
| -12% trailing loss triggered exits | 26 |
| Six-month deadline exits | 9 |
| **Non-executable $0 recovery write-offs** | **5** |
| New buys in 2026 | **0** |
| Last held stock sold in simulation | **2026-02-17** |
| Final inventory at June cutoff | **0** |

**Exception register (NOT actual sales):** MON-201806 (2018-06-20), FOX-201903 and FOXA-201903 (2019-04-02), RHT (2019-07-22), TIF (2021-01-21). For all five, executable next-open proceeds were not verified and the simulator imposed a **zero-recovery write-off**. This can materially depress the strategy outcome. The trade ledger preserves the exact share units, prices and event labels needed for follow-up settlement research.

**Signal discipline:** capital deployed only after prior-close decisions; one-day execution gaps can overshoot stop/profit thresholds; as-of S&P 500 membership and known untraded days are used. Static default thresholds and policy score chosen ex post remain a material research-design limitation.

## Raw files

| Evidence | File |
|:--|:--|
| Machine-readable full summary, data SHA256s and caveats | [summary.json](proxy/summary.json) |
| Exact individual simulated purchases/exits and exceptions | [trades.csv](proxy/trades.csv) |
| Daily equity, cash, positions and selected entry profile | [equity_curve.csv](proxy/equity_curve.csv) |
| Annual NAV and matching benchmark returns | [yearly.csv](proxy/yearly.csv) |
| Effective policy dates, prior training cutoff and shadow ranking | [policy_log.json](proxy/policy_log.json) |
| Simulation implementation | [backtest.py](../backtest.py) |
| Reproducibility workflow | [GitHub Actions](../../../.github/workflows/swing-2018-2026-walkforward.yml) |

## Evidence and caveats

Source: [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data), publicly versioned prices and historical member snapshots (exact downloaded hashes recorded in JSON). Reconstructed historical members reduce but cannot eliminate survivorship/data-vintage bias. Adjusted prices can be restated; no independently verified corporate-action payouts. The strict fundamental/news mode is **not run** because the repository contains only schema headers for those inputs. Sector peers are not documented direct competitors. No claim of historic absence of material negative news is made.

The **2018 development** period is in-sample. The subsequent replay respects chronological policy selection *inside the backtest*, but all profile definitions were devised in 2026 after the entire historic era. Therefore performance should not be advertised as an untouched OOS alpha validation.

[← Specification](../README.md) · [← All results](../../../docs/RESULTS.md)
