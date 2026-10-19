# S-01 · Medium-term trading · 2024–2025

[← Experiments](../README.md) · [All results](../../docs/RESULTS.md) · [Data caveats](../../docs/DATA_QUALITY.md)

> [!NOTE]
> **COMPLETE · 502 daily market sessions.** A fresh **$100,000** account is simulated starting January 2024. This is the **standalone two-year** study and must not be confused with a six-year portfolio's 2024–2025 segment.

## 01 / Research question

How did a simple **historical top-100 dollar-liquidity** S&P 500 basket perform using sell-off reversals or confirmed trends, with a maximum holding period of four months? This is a technical **proxy** study—not a confirmed valuation-based or news-filtered experiment.

## 02 / Experiment design

| Property | Setting |
|:--|:--|
| Date range | **2024-01-02 → 2025-12-31** |
| Universe | The **100 most liquid** contemporaneous index members, ranked on the final December session of the previous year |
| Historic cap top 100? | **No**, this is dollar-volume ranking rather than capitalization ranking |
| Data | Historical S&P 500 membership and split/dividend-adjusted daily prices |
| Strategy variants | **Original v1**; **route-aware v1.1 (post-hoc)** |
| Benchmark | Same-window dividend-adjusted **SPY** |

## Shared signal and execution rules

| Component | Fixed rule |
|:--|:--|
| Starting account | **$100,000**; no leverage; idle cash earns 0% |
| Liquidity filter | Last 63 sessions' average dollar turnover **>$20 million** |
| Stock volatility filter | Trailing 63-session annualized volatility **<=65%** |
| Price filter | Adjusted close **>$5** |
| **Sell-off** entry | 5-session drop **<=-10%**, >=7pp weaker than SPY, SPY 5-day change >-4% |
| **Reversal** confirmation | RSI14 <48, positive close >=2% above 3-day low, adjusted close >90% of SMA200, prior gap >-6% |
| **Trend** entry | Close > SMA20 > SMA50 > SMA200; RSI14 between 48–68; within 6% of 63-day high |
| Fill timing | Signal on **previous close**, simulated trade on **next session's open** |
| Fee and slippage | **6 basis points per side**, modeled |
| Position sizing | Max **10** holdings; new name <=12% of account equity |
| Gross exposure | <=90% if SPY above SMA200; otherwise <=60% |
| Universal exits | -8% from entry, -12% trailing peak close, +20% and RSI14>72, index deletion, or **four calendar months** |
| Original `v1` exit | Prior close <97% SMA50 and down day causes exit on **both** signal types |
| Route-aware `v1.1` exit | That SMA50 exit only on trend positions; reversal exits at +6% plus reclaimed SMA20 |

> [!CAUTION]
> The numerical stop levels are **previous-close triggers**, not guarantees of the next-open execution price. The “unexplained 10% decline” condition cannot be established from prices alone, and executed proxy runs did **not** use timestamped P/E / EV/EBITDA / FCF multiples or news verification. Route-aware exits were defined after analyzing 2024–2025; they are post-hoc.


## 03 / Confirmed results

| Outcome | Original / v1 | Route-aware / v1.1 |
|:--|--:|--:|
| Ending NAV | **$117,476.38** | **$117,083.67** |
| Cumulative return | +17.48% | +17.08% |
| CAGR | +8.40% | +8.22% |
| Maximum drawdown | -14.19% | -14.71% |
| Sharpe (0% risk-free) | 0.860 | 0.830 |
| Completed round trips | 104 | 100 |
| Realized win rate | 37.50% | 38.00% |
| SPY matched return | **+47.99%** | **+47.99%** |

The earlier baseline outperformed the edited variant slightly **within this very sample**, and both underperformed SPY by more than 30 percentage points. These findings are descriptive, not a claim of statistical significance.

**[Open results directory →](results/README.md)** · [Original run report](results/proxy/README.md) · [Route-aware run report](results/proxy_route_aware/README.md)

## 04 / Interpretation & detailed findings

The original 2024–2025 simulation recorded **114 buys**, **106 trend entries** and only **8 reversal entries**. The strategy's return therefore primarily reflects the technical-trend sleeve. Applying the trend break exit to the reversal sleeve created a structural mismatch; the revised route-aware rule attempted to address it **after observing historical failures**.

- [Original realized trade diagnostics](RESULTS_ANALYSIS.md)
- [Exact rationale, version history and v1.1 comparison](REVISION_V1_1.md)

## 05 / Reproduction

```bash
python -m pip install -r experiments/medium_term_2024_2025/requirements.txt

# Current backtest.py is v1.1 / route-aware.
python experiments/medium_term_2024_2025/backtest.py --mode proxy --out /tmp/medium_2024_2025_route
```

> [!IMPORTANT]
> The **original v1** result comes from the earlier source revision [**1c8fa41**](https://github.com/HyeonbinJung/2025-Intraday-Walkforward-Backtest/blob/1c8fa41cca72b2bfa35b155e7e6a9529f100e460/experiments/medium_term_2024_2025/backtest.py). The current script should **not** be cited as the exact original-v1 replay engine. Do not overwrite published `results/` paths when reproducing.

For strict research with **historical capitalization top 100 and valuation gates**, the source accepts `--mode full`, requiring authentic dated `input/top100_pit.csv` and `input/valuation_pit.csv`. These are unpopulated templates; **no valid full fundamental result is currently reported**.

## 06 / Evidence & limitations

| Evidence | Link |
|:--|:--|
| Original summary JSON | [2024–2025 / proxy](results/proxy/summary.json) |
| Route-aware summary JSON | [2024–2025 / route-aware](results/proxy_route_aware/summary.json) |
| Trade ledgers | [Original](results/proxy/trades.csv) / [Revised](results/proxy_route_aware/trades.csv) |
| Published workflow | [GitHub Actions YAML](../../.github/workflows/medium-term-2024-2025.yml) |

Historical prices may be revised after publication, full historical valuation and negative-news explanations were not provided, and fixed-next-open fills are simplified. [Detailed integrity register](../../docs/DATA_QUALITY.md).
