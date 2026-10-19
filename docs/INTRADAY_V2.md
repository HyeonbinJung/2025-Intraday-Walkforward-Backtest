# I-02 · Intraday lower-turnover replay (v2)

[← Experiment catalog](../experiments/README.md) · [Results checkpoint](../results/2025H1_v2/README.md) · [Project home](../README.md)

> [!WARNING]
> **PARTIAL experiment** — only the first historical batch (2025-01-01 → 2025-01-14) is committed. **8 of 122 requested NYSE sessions**, checkpoint equity **$97,551.06**; no verified June 2025 closing NAV or six-month return.

## Research question

Could lower turnover and more conservative switching reduce the excessive transaction-cost drag observed in the original one-minute system? The baseline lost 59.19% over completed 2025H1 with about $48,052 estimated transaction cost. A single early v2 checkpoint **cannot** answer the full six-month question.

## Experimental design

| Parameter | v2 |
|:--|:--|
| Requested period | 2025-01-01 → 2025-06-30 |
| Observed completed period | 2025-01-01 → 2025-01-14 |
| Data | Historical minute OHLCV, NYSE calendar |
| Initial account | $100,000 |
| Latest committed checkpoint | **$97,551.06** |
| Status | **PARTIAL**, 8/122 trading sessions |
| Rules evaluated | Every completed minute |
| Fill timing | No earlier than the following minute open |
| Execution costs | 5bp estimated slippage per side + $0.005/share |
| Volume cap | <=1% of previous bar's observed volume |

## Revision parameters from source

`experiments/v2_2025H1/engine_v2.py` initializes:

| Control | Source value | Intent |
|:--|--:|:--|
| Minimum hold | 10 minutes | Avoid instant position churn |
| Rebalance interval | 10 minutes | Avoid continuous reshuffling |
| Daily fill cap | 80 | Lower order count |
| Selection margin | 0.006 | Add a switching hurdle |

These controls are present in code; **do not infer the six-month result from parameters alone**.

## Evidence and outputs

- [Committed partial summary JSON](../results/2025H1_v2/summary.json) · [Checkpoint](../results/2025H1_v2/state.json)
- [First batch and evidence ledger](../results/2025H1_v2/batches/2025-01-01_to_2025-01-14/)
- [Replay implementation](../experiments/v2_2025H1/batch_replay_v2.py) · [Core engine](../experiments/v2_2025H1/engine_v2.py)
- [Original replay postmortem](../results/2025H1/POSTMORTEM_AND_V2_PROMPT.md)

Do not place a v2 six-month CAGR, Sharpe, June NAV or 'strategy wins' headline here until all expected sessions and coverage checks pass.

## Reproduction

```bash
python -m pip install -r requirements.txt
python experiments/v2_2025H1/batch_replay_v2.py --batch-start 2025-01-01 --batch-end 2025-01-14 --out /tmp/replay_v2
```

Run later contiguous calendar batches in a fresh directory. [Automated workflow](../.github/workflows/replay-2025-v2.yml) is available but completion must be verified via `results/2025H1_v2/summary.json`.

See [data quality caveats](DATA_QUALITY.md) for source/corporate-action and minute-fill limitations.
