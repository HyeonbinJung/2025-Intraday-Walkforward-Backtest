# Data integrity & disclosure register

[← Research documentation](README.md) · [Results](RESULTS.md) · [Reporting standards](STYLE_GUIDE.md)

> [!CAUTION]
> **Backtest completion != independently verified, tradable return.** All recorded account values are simulation outputs. The price-only experiments cannot be presented as verified valuation-based investment systems.

## Data source register

| Research family | Observed data | Historical scope | Source-specific caveat |
|:--|:--|:--|:--|
| One-minute intraday | Minute OHLCV, NYSE calendar | Jan–Jun 2025 | Third-party archive, may have missing symbols/survivorship, split-adjustment uncertainty |
| Daily medium term | Historic S&P 500 snapshots and adjusted OHLCV | 2020–2025, 2024–2025 | Rebuilt/reconciled in 2026; adjusted price may be restated ex post |
| Benchmarks | Dividend-adjusted SPY | Matched daily strategy dates | Not fee/beta/exposure matched; SPY comparison is buy-and-hold |
| Adaptive six-month swing S-04 | Historic daily S&P 500 prices / membership; optional externally supplied dated fundamentals and news | 2018–June 2026 | Prices repaired retrospectively; default proxy validates NEITHER historic fundamentals/competitors NOR negative-news absence; zero-recovery writeoffs are non-executable |

Source repositories: [mito0o852/OHLCV-1m](https://huggingface.co/datasets/mito0o852/OHLCV-1m) and [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data). A data feed with point-in-time *index membership* is not automatically a point-in-time feed for *all fundamental estimates*.

## Known limitations & severity

| Issue | Affected experiments | Disclosure / required improvement |
|:--|:--|:--|
| **Historical valuation unavailable** | All automated daily backtests | P/E, EV/EBITDA, FCF yield etc. were **not measured** as trading filters; full test requires dated as-filed values |
| **"No reason" for 10% fall unverified** | Daily reversal entries | Negative earnings/news/management guidance/sector shocks can explain a fall; needs contemporaneous news/filing screening |
| **Historical cap ranking unavailable** | Daily top-100 experiments | The 100 names are chosen by **dollar liquidity**, **not market cap** |
| **Unverified corporate action payout** | Six-year daily accounts | 2 synthetic settlements in liquid-100, 8 in all-index experiments; not filled at a real execution price |
| **Data vintage after test window** | Historical price datasets | Retroactively cleaned adjusted OHLCV may differ from information available on the trade date |
| **Execution approximation** | All | Next bar/open, fixed model slippage; cannot replicate spread, quote depth, auction participation, gap fills or stock halts completely |
| **Intraday source biases** | Minute replay | Historical symbol selection, delisted names and corporate actions may have missing/unusable bars |
| **Training/evaluation overlap** | Route-aware exit | Rule revision follows study of 2024–2025; do not report 2020–2025 as fresh, untouched OOS |
| **Short/incomplete sample** | Intraday v2 | 8/122 sessions; no six-month result, no valid full-period return or annualization |
| **Sector and factor concentration** | All daily | No sector-constrained portfolio construction; risk differs from SPY, beta comparison needed |

## Corporate-action assumptions in six-year results

The larger historical universe triggers **eight** last-adjusted-price **synthetic settlements** across both exit variants:

| Label | Recorded simulation date | Synthetic adjusted mark |
|:--|:--|--:|
| TIF | 2021-01-07 | 131.46 |
| VAR | 2021-04-20 | 177.07 |
| FLIR | 2021-05-14 | 57.34 |
| ALXN | 2021-07-21 | 182.50 |
| CERN | 2022-06-08 | 94.92 |
| CTXS | 2022-10-03 | 103.90 |
| WBA | 2025-08-28 | 11.98 |
| K | 2025-12-11 | 83.44 |

**Important:** these values are in the model's adjusted share-unit convention, **not** necessarily actual merger cash consideration, raw settlement dollars, or trade prices. They need event-document reconciliation before P&L claims of real-world feasibility. The 100-liquid universe has 2 separate synthetic settlements (TIF, PXD). Do not delete or recode these assumptions as normal SELL orders in analysis.

## What is validated vs unverified?

| Claim | Evidence status |
|:--|:--|
| Original intraday 2025H1 historical replay completed 122 sessions | **Verified within stored summary** |
| Intraday v2 completed all 2025H1 sessions | **False / partial (8 of 122)** |
| Daily 2020–2025 runs completed 1,508 sessions | **Verified within stored summaries** |
| The 100-name basket consists of 100 largest stocks by market cap | **Not supported** |
| Falls of >=10% had no fundamental negative explanation | **Not supported** |
| Historical price-only results reflect a properly backtested value factor | **Not supported** |
| Every daily exit represents an executable sale at the printed adjusted close | **Not supported** |
| A winning trading strategy beat SPY from 2020 to 2025 | **False under stored simulated results** |

## Required audit work before drawing investability conclusions

1. Obtain historical market-cap ranking for each applicable past December.
2. Obtain as-published fundamentals, historic share counts and dated enterprise-value inputs.
3. Audit news/earnings/events in timestamped form at each reversal entry.
4. Replace eight synthetic settlements with actual, documented cash/stock consideration (including adjusted-share convention).
5. Independently source-check adjusted opens, split/dividend treatment, delisted stocks and any historical zero-volume sessions.
6. Measure realized exposure, sector concentration, market beta, turnover, and spread stress cases.
7. Declare a genuinely unused period for forward-style validation. Do not optimize thresholds on the same evaluated 2020–2025 observations.

[← Back to results](RESULTS.md)
