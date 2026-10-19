# Research methodology & reproducibility

[← Project home](../README.md) · [Experiment catalog](../experiments/README.md) · [Results](RESULTS.md)

## At the system boundary

The repository contains two **distinct** simulation systems. The algorithms and their P&L figures must not be presented as if they were the same execution strategy.

| Property | Minute replay (I-01 / I-02) | Medium-term backtests (S-01 / S-02 / S-03) |
|:--|:--|:--|
| Data granularity | Completed 1-minute OHLCV bars | Daily historical OHLCV |
| Signal evaluation | After each minute completes | After previous day close |
| Earliest assumed fill | Following minute open | Following session open |
| Portfolio base | $100,000 | $100,000 |
| Position budget | Intraday risk logic; see versioned engines | 10 holdings; max 12% per new position |
| Costs | 5bp slippage **plus** $0.005/share commission | 6bp **per side** total |
| Time horizon | 2025 Jan–Jun | 2024–25 or 2020–25 |
| Data feed | [1-minutes dataset](https://huggingface.co/datasets/mito0o852/OHLCV-1m) | [Historical constituents/prices](https://github.com/Johnbrick123/sp500-data) |
| Completion condition | Valid 14-day batches + expected NYSE sessions | Complete date range, annual universe and saved summary |

## Minute replay strategy

**Original I-01** uses minute-close signal and risk reevaluation, short-horizon momentum/relative-volume ranking, next-minute open fills, volume participation cap and periodic 10-minute persisted snapshots. Loss-adaptive parameters are based on recorded realized results. The original simulation resulted in very high turnover.

**I-02 lower-turnover revision** retains the basic minute OHLCV input and re-evaluation cadence, but adds controls found in [engine_v2.py](../experiments/v2_2025H1/engine_v2.py) including `minimum_hold_minutes=10`, `rebalance_interval=10`, `max_daily_fills=80`, and `selection_margin=0.006`. The v2 output is **PARTIAL** (only the first batch is committed): neither a complete 2025H1 portfolio nor a full-period numerical comparison exists. [Detailed v2 notes](INTRADAY_V2.md).

### Reproduce the intraday experiment

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
# Always use a NEW output directory so a replay cannot corrupt published evidence.
python src/batch_replay.py --batch-start 2025-01-01 --batch-end 2025-01-14 --out /tmp/replay_2025H1
```

Later batches must be **contiguous** with the checkpoint `last_batch_end` date. GitHub Actions workflows [original](../.github/workflows/replay-2025.yml) and [v2](../.github/workflows/replay-2025-v2.yml) exist for their respective engines. The workflow's existence is not proof of a currently running process.

## Daily medium-term strategy · common rules

### Eligible candidates and signals

Each model screens its permitted historical S&P 500 member set. The *annual dollar-liquidity 100* version freezes the candidate list at the previous year's final session; the *full-index* model recomputes actual index membership by signal date.

| Rule | Threshold |
|:--|:--|
| Minimum stock price | Above $5 adjusted |
| Liquidity | 63-day average daily traded value above $20 million |
| Annualized daily volatility | 63-day realized volatility <=65% |
| Reversal candidate | 5-session return <= -10%; >=7pp behind SPY; SPY > -4% |
| Reversal confirmation | Rebound >=2% from 3-day low, green day, RSI14 <48, close >90% SMA200; opening gap > -6% |
| Trend candidate | close > SMA20 > SMA50 > SMA200; RSI14 48–68; within 6% of 63-day high |

Valuation filters **only exist as optional code paths** requiring externally supplied point-in-time inputs. Executed historical studies use `--mode proxy`, *without* those data. "Reasonless fall" is not verifiable from price bars alone.

### Execution & exits

- Simulated fill no earlier than next day's synthetic dividend-adjusted open.
- Gross allocation max 90% when SPY > SMA200 or 60% otherwise.
- No leverage, interest on cash, or taxes; 6bps per transaction side.
- Triggered at previous close: -8% vs entry, -12% trailing high, +20% and RSI14 >72, S&P membership deletion, or mandatory exit at first tradable session >=entry date + four calendar months. Stop trigger does not guarantee an 8% executed loss.
- **Original exits**: SMA50 close decline with a down day liquidates both trend and reversal holdings.
- **Route-aware exits**: SMA50 decline liquidates trend holdings; reversal holdings exit on >=6% gain plus SMA20 reclaim. This second version was **post-hoc** and must not be framed as untouched out-of-sample validation.
- Missing merger consideration / untradable delisting: synthetic last adjusted close is recorded as a **non-executable accounting proxy**, not a real sale.

### Reproduce the six-year daily models

```bash
python -m pip install -r experiments/medium_term_2020_2025/requirements.txt
python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode original --out /tmp/liquid100_original
python experiments/medium_term_2020_2025/backtest.py --mode proxy --exit-mode route_aware --out /tmp/liquid100_route

python -m pip install -r experiments/medium_term_2020_2025_sp500/requirements.txt
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode original --out /tmp/all500_original
python experiments/medium_term_2020_2025_sp500/backtest.py --mode proxy --exit-mode route_aware --out /tmp/all500_route
```

**Use separate output paths** for different experiments; a repeated run into an existing path can overwrite machine-derived files. They fetch historical source archives and can consume network bandwidth.

### Data files and provenance

| File | Meaning |
|:--|:--|
| `summary.json` | Machine-readable run status, period, rules version and aggregate P&L |
| `equity_curve.csv` | Daily account equity and positions |
| `monthly.csv` | Month-by-month percentage returns |
| `trades.csv` | Entry, exit, reason and cost line items |
| `results/2025H1/batches/*` | Minute replay ledger: coverage, rules, minute and 10-minute snapshots |
| `state.json` | Resumable current portfolio / engine checkpoint |

## What a credible improvement test requires

Freeze new rules **before** testing a genuinely unused period. Check performance after realistic transaction costs, compare SPY for the *identical dates*, report maximum drawdown and exposure, verify actual historical company survivorship and merger consideration, and ideally benchmark risk-adjusted rather than merely cumulative returns.

[Data integrity checklist →](DATA_QUALITY.md)
