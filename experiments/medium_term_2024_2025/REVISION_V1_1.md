# Version 1.1: entry-route-aware exits (post-hoc structural repair)

This revision was **motivated by diagnostics on the full 2024–2025 sample**, so the 2024–2025 performance of v1.1 is **in-sample** and MUST NOT be represented as an independent forward/walk-forward validation.

The first, pre-revision backtest and its analytics remain under results/proxy and RESULTS_ANALYSIS.md. It showed 8 sell-off-reversal entries out of 114 total; all 8 got exited by the technical-trend MA50 rule, generally within one or two sessions. The 50-day trend-following exit is a logical mismatch for entering an oversold mean-reverting stock below its moving averages.

**Change (only exit routing):**
- Trend entries: keep original MA50 broken rule (prior close below 97% SMA50 plus red session), hard -8% close stop, -12% trailing, profit RSI filter, and 4-calendar-month maximum.
- Dip-reversal entries: skip the incompatible SMA50 trend exit; take a mean-reversion exit once prior close is **at least +6% above entry AND at or above 20-day SMA**. Keep -8% stop, -12% trailing, profit RSI filter, and 4-month exit.
- 100-name annual dollar-volume **proxy** universe, no verified value/news, next open fills and 6bp per side unchanged.

v1.1 outputs use results/proxy_route_aware. Any difference between versions is **only a same-sample engineering comparison**. Real validation needs a fresh 2026-forward out-of-sample period or earlier training years, fixed splits and a truly point-in-time market-cap/valuation/news feed.

No causal claim that 'reasonless' declines were identified.
