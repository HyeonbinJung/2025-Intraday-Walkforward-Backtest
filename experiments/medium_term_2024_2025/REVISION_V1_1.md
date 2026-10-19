# Version 1.1: entry-route-aware exits (post-hoc structural repair)

This revision was **motivated by diagnostics on the full 2024–2025 sample**, so the 2024–2025 performance of v1.1 is **in-sample** and MUST NOT be represented as an independent forward/walk-forward validation.

The first, pre-revision backtest and its analytics remain under results/proxy and RESULTS_ANALYSIS.md. It showed 8 sell-off-reversal entries out of 114 total; all 8 got exited by the technical-trend MA50 rule, generally within one or two sessions. The 50-day trend-following exit is a logical mismatch for entering an oversold mean-reverting stock below its moving averages.

**Change (only exit routing):**
- Trend entries: keep original MA50 broken rule (prior close below 97% SMA50 plus red session), hard -8% close stop, -12% trailing, profit RSI filter, and 4-calendar-month maximum.
- Dip-reversal entries: skip the incompatible SMA50 trend exit; take a mean-reversion exit once prior close is **at least +6% above entry AND at or above 20-day SMA**. Keep -8% stop, -12% trailing, profit RSI filter, and 4-month exit.
- 100-name annual dollar-volume **proxy** universe, no verified value/news, next open fills and 6bp per side unchanged.

v1.1 outputs use results/proxy_route_aware. Any difference between versions is **only a same-sample engineering comparison**. Real validation needs a fresh 2026-forward out-of-sample period or earlier training years, fixed splits and a truly point-in-time market-cap/valuation/news feed.

No causal claim that 'reasonless' declines were identified.

## Verified run outcomes (both 502 trading days)

| Metric | v1 original frozen proxy | v1.1 route-aware, post-hoc |
|---|---:|---:|
| Ending account | $117,476.38 | **$117,083.67** |
| Full-period return | +17.476% | **+17.084%** |
| 2024 return | +19.805% | +20.028% |
| 2025 return | -1.944% | -2.453% |
| Maximum drawdown | -14.193% | -14.712% |
| Closed round trips | 104 | 100 |
| Win rate | 37.50% | 38.00% |
| SPY cumulative return | +47.990% | +47.990% |

The structural repair did **not** improve net historical account return; it underperformed v1 by 0.392 percentage points and SPY by 30.906 percentage points. It was *not* selected through return optimization. Six route-aware dip-reversal entries occurred (versus eight in v1); four exits were triggered by DIP_RECOVERED and closed at mean +7.63%. Those are a small in-sample set, not proof of a repeatable advantage.

Source: GitHub Actions success for revision v1.1; raw files in results/proxy_route_aware. The unchanged first-pass data remain in results/proxy.
