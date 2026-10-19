# S-03 · Medium-term trading · full historical S&P 500 (2020–2025)

[← Experiments](../README.md) · [All results](../../docs/RESULTS.md) · [Compare 100 vs 500](RESULTS_COMPARISON.md)

> [!NOTE]
> **COMPLETE · 1,508 sessions.** Each signal date screens **all contemporaneous S&P 500 constituents** (about 503–508 tickers in this source), not just the historical prior-year-dollar-liquidity top 100. The actual portfolio still holds **no more than 10 stocks**.

## 01 / Research question

Does broadening the eligible candidate list from **100 liquid S&P 500 stocks** to **all historical S&P 500 members** improve performance **without changing** the initial signal, risk and exit criteria?

## 02 / Experimental design

| Property | Setting |
|:--|:--|
| Window | **2020-01-02 → 2025-12-31** |
| Eligible universe | **All index constituents on each signal day** |
| Membership history | As reconstructed in historical constituent snapshots |
| Starting capital | **$100,000** |
| Portfolio | At most **10 long positions** |
| Variants | Original v1 and route-aware v1.1 (post-hoc) |
| Comparison | [S-02 / 100 by dollar liquidity](../medium_term_2020_2025/README.md) |
| Benchmark | Dividend-adjusted SPY buy-and-hold |

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

| Outcome | 500 candidates / Original | 500 candidates / Route-aware | 100 / Original | 100 / Route-aware |
|:--|--:|--:|--:|--:|
| Ending NAV | $106,429.99 | **$124,601.04** | $124,373.08 | $124,008.34 |
| Cumulative return | +6.43% | **+24.60%** | +24.37% | +24.01% |
| CAGR | +1.05% | +3.74% | +3.71% | +3.65% |
| Maximum drawdown | -22.20% | -25.08% | -23.54% | -24.30% |
| Win rate | 37.82% | 41.82% | 36.18% | 36.12% |
| Closed trades | 349 | 330 | 340 | 335 |

**SPY: +130.14%** over the identical 2020–2025 window. Scanning 500 candidates alone **did not** generate market-beating performance. The original exit rules performed significantly worse with the larger universe; route-aware results were similar to the smaller basket.

**[Results index →](results/README.md)** · [Original results](results/original/README.md) · [Route-aware results](results/route_aware/README.md) · [Full annual breakdown](RESULTS_COMPARISON.md)

## 04 / Main findings

- Original 500-stock run: **328 trend entries, 31 reversal entries**.
- Route-aware 500-stock run: **312 trend entries, 28 reversal entries**.
- Expanding the scanner increases dip opportunity count, but the strategies remain dominated by technical trends and **do not represent a validated cheap-valuation/no-news study**.
- **Eight historical M&A/delisting exits per variant** were synthetically settled because next-open tradable proceeds were not verified. These are explicitly flagged, **not** executable historical fills.

[Detailed historical comparative analysis →](RESULTS_COMPARISON.md)

## 05 / Reproduce

```bash
python -m pip install -r experiments/medium_term_2020_2025_sp500/requirements.txt
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode original --out /tmp/500_original
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode route_aware --out /tmp/500_route
```

Run commands from the repository root. Outputs go to distinct directories so existing committed results remain intact. [Automation workflow](../../.github/workflows/medium-term-2020-2025-sp500.yml).

## 06 / Evidence & limitations

| Record | Link |
|:--|:--|
| Original summary | [summary.json](results/original/summary.json) |
| Route-aware summary | [summary.json](results/route_aware/summary.json) |
| Original order log | [trades.csv](results/original/trades.csv) |
| Route-aware order log | [trades.csv](results/route_aware/trades.csv) |
| Source implementation | [backtest.py](backtest.py) |

The index member history prevents reliance solely on *today's* survivors but not every data-vintage bias. Source prices were assembled/reconciled after the trading years; slippage, historical corporate settlements and event-news assumptions are simplified or unknown. [Integrity checklist](../../docs/DATA_QUALITY.md).
