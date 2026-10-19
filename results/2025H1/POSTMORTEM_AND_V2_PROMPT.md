# I-01 · Intraday baseline postmortem and next experiment

[← Completed 2025H1 result](README.md) · [Monthly report](MONTHLY_REPORT.md) · [v2 checkpoint](../2025H1_v2/README.md)

> [!CAUTION]
> The completed January–June 2025 intraday simulation **lost 59.19%**. Its revision v2 is currently **PARTIAL** (8 of 122 sessions), and there is **no completed v2 six-month result**.

## 01 / Evidence snapshot

| Metric | Measured from completed I-01 run |
|:--|--:|
| Starting capital | $100,000.00 |
| Ending capital | **$40,809.57** |
| P&L | **-$59,190.43** |
| Total return | **-59.19%** |
| Trading sessions | 122 / 122 |
| Fill records | 31,241 |
| Estimated modeled fees & slippage | **$48,052.35** |
| Fill records per session | ~256.07 |
| Trading-cost magnitude / initial capital | **48.05%** |

The cost sum equals about **81.18% of the absolute magnitude of the reported loss**. This ratio is *not* a cost-only counterfactual; the model's trades and returns could have differed without the fees.

## 02 / Failure hypothesis register

| Priority | Hypothesis | Supporting implementation evidence | What must be tested |
|:--|:--|:--|:--|
| **High** | Excessive churn and re-selection | Position target reset every completed minute; no minimum hold/hysteresis/daily turnover cap in original engine | Turnover, hold-time distribution, gross/net attribution |
| **High** | No net-cost return hurdle | Scores rely on recent returns, relative volume and volatility rather than explicit forecast less fees/slippage | Net edge per signal at time of order |
| **High** | Inadequate adaptive-risk design | Losing partial sell fills affect streak logic; shrinking risk does not fix strategy family or turnover | Round-trip based loss counts, state changes |
| **Investigate** | Momentum reversals/regime mismatch | Short-lived volume spikes may mean revert after entry | Signal cohort / forward-return attribution |
| **Known limitation** | Simplified execution/data adjustments | Next-minute OHLCV-open fill, 1% previous-minute participation, fixed spread/slippage; possible historic symbol bias | Alternate spread/impact assumptions and independent data |

**None of these factors alone is a proven causal decomposition of the entire -59.19%.** The first three are code-grounded concerns; momentum regime is a hypothesis.

## 03 / Prioritized follow-up analysis

1. Preserve the original engine and 13 committed batch results as the baseline.
2. Report *gross versus net* P&L by month, symbol and position, fill count, turnover, holding duration and average spread/cost assumptions.
3. Ablate **one change at a time**: 5/10/20-minute minimum holding, ranking hysteresis, 10/30/60-minute rebalancing, daily order budgets, and market/volatility filters.
4. Correct loss-streak counting from partial sell fills to closed **position-level** round trips, and add deterministic unit tests.
5. Test net-of-cost entry hurdles and execution sensitivity rather than optimizing only gross momentum scores.
6. Set time-ordered train/validation/test windows with purging/embargo where relevant; compare SPY, cash and low-turnover baselines on matched periods and costs.
7. Document every failure as well as any improvement; a new strategy only counts as supported when held-out evidence is available.

## 04 / Reusable research brief

> Keep the original 2025H1 strategy code and committed results immutable. Diagnose the -59.19% baseline with reproducible month/symbol cost attribution, holding-time distributions, fill counts and risk-event analysis. Implement lower-turnover features as separately switchable ablations: minimum hold, ranking hysteresis, daily turnover limit, expected net-return hurdle and round-trip loss counting. Use chronological, no-look-ahead testing with a genuinely reserved final holdout, independent price/corporate-action checks, realistic slippage/spread assumptions and clear SPY/cash benchmarks. Store source, configuration, each run's raw CSV/JSON, and a comparative Markdown report in separate experiment directories. Do not overwrite the baseline or claim an improvement without complete out-of-sample evidence.

## 05 / Original evidence trail

[2025H1 summary](summary.json) · [Daily/batch ledgers](batches/) · [Monthly equity](MONTHLY_REPORT.md) · [v2 status and parameters](../../docs/INTRADAY_V2.md) · [System limitations](../../docs/DATA_QUALITY.md).
