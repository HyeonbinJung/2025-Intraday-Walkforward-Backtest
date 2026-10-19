# S-02 · Medium-term trading · 2020–2025 (100 liquid names)

[← Experiments](../README.md) · [All results](../../docs/RESULTS.md) · [Data caveats](../../docs/DATA_QUALITY.md)

> [!NOTE]
> **COMPLETE · 1,508 trading sessions.** A continuously simulated $100,000 account runs for **six full calendar years**. Positions and cash **carry forward** each year; the 2024–2025 subperiod is not the separate S-01 fresh-start account.

## 01 / Research question

Does extending the same rules-based swing framework back through **2020–2025** provide more credible evidence of its performance across different market regimes? **This is still technical price-only proxy research.**

## 02 / Experiment design

| Property | Setting |
|:--|:--|
| Window | **2020-01-02 → 2025-12-31** |
| Universe | Prior-year-end **top 100 by trailing 63-session dollar trading volume** among historic S&P 500 members |
| 100 largest market caps? | **No**; size and dollar-volume rank are not the same thing |
| Annual candidate refresh | Re-ranked at each prior December session |
| Data warm-up | 2018–2019 pricing history |
| Exits | Original v1 and route-aware v1.1 (post-hoc) |
| Matched benchmark | SPY total-return adjusted prices |

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


## 03 / Six-year results

| Metric | Original v1 | Route-aware v1.1 |
|:--|--:|--:|
| Ending NAV | **$124,373.08** | **$124,008.34** |
| Cumulative return | +24.37% | +24.01% |
| CAGR | +3.71% | +3.65% |
| Max drawdown | -23.54% | -24.30% |
| Sharpe (0% risk-free) | 0.353 | 0.347 |
| Realized win rate | 36.18% | 36.12% |
| Completed trades | 340 | 335 |
| **SPY cumulative return** | **+130.14%** | **+130.14%** |

### Calendar-year returns

| Year | Original v1 | Route-aware v1.1 | SPY |
|:--|--:|--:|--:|
| 2020 | +6.08% | +6.86% | +18.37% |
| 2021 | +22.03% | +22.03% | +28.74% |
| 2022 | -11.78% | -12.39% | -18.17% |
| 2023 | +7.16% | +5.12% | +26.19% |
| 2024 | +8.47% | +11.26% | +24.89% |
| 2025 | -6.31% | -7.19% | +17.72% |

**[Open results index →](results/README.md)** · [Original results](results/original/README.md) · [Route-aware results](results/route_aware/README.md)

## 04 / Main findings

In the original six-year run, **339 out of 350 purchases were trend entries**, with **only 11 reversal entries**. The system thus does not substantively measure the requested "buy an unexplained 10% drop at attractive multiples" thesis. The strategy protected more capital than SPY in some down markets, but the six-year portfolio **underperformed SPY significantly**.

[Detailed entry/exit attribution](RESULTS_ANALYSIS.md) · [Cross-universe comparison](../medium_term_2020_2025_sp500/RESULTS_COMPARISON.md)

## 05 / Reproduce

```bash
python -m pip install -r experiments/medium_term_2020_2025/requirements.txt
python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode original --out /tmp/100_original
python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode route_aware --out /tmp/100_route
```

The historical **PIT market-cap** and as-filed valuation mode exists as optional code but requires populated and validated `input/top100_pit.csv` and `input/valuation_pit.csv`. These inputs are not provided as verified historical records. [Run workflow](../../.github/workflows/medium-term-2020-2025.yml).

## 06 / Evidence & limitations

| Record | Location |
|:--|:--|
| Original machine summary | [summary.json](results/original/summary.json) |
| Route-aware machine summary | [summary.json](results/route_aware/summary.json) |
| Orders | [Original](results/original/trades.csv) / [Route-aware](results/route_aware/trades.csv) |
| Daily account curves | [Original](results/original/equity_curve.csv) / [Route-aware](results/route_aware/equity_curve.csv) |

**Two synthetic non-executable acquisition exit assumptions** (TIF and PXD) appear in each six-year portfolio. These were valued at prior adjusted price, not verified historical merger cash/stock settlement. This and ex-post price-vintage issues matter for actual deployability. [Read data quality limitations](../../docs/DATA_QUALITY.md).
