# I-02 · 2025H1 low-turnover revision · partial checkpoint

[← Intraday results](../README.md) · [v2 research note](../../docs/INTRADAY_V2.md) · [Project home](../../README.md)

> [!WARNING]
> **PARTIAL / 8 of 122 NYSE sessions.** The latest successfully committed batch ends **2025-01-14**. **No validated June 30, 2025 equity or six-month return exists** for this revision.

## Published checkpoint (not a final result)

| Field | Committed value |
|:--|--:|
| Start equity | $100,000.00 |
| Current January 14 checkpoint | **$97,551.06** |
| Requested evaluation end | 2025-06-30 |
| Last completed batch end | 2025-01-14 |
| Covered / expected sessions | **8 / 122** |
| Completed replay batches | 1 |
| Fill records so far | 705 |
| Completed minute rule checks | 3,120 |
| Estimated cumulative transaction costs | $1,468.88 |
| Full six-month P&L and return | **Not available** |

## Scope of v2

The [v2 engine](../../experiments/v2_2025H1/engine_v2.py) adds minimum holding time, reassessment intervals, fill limits and a switching margin. The historical snapshot is too short to establish whether the lower-turnover rules improve completed-period performance versus I-01.

## Source files

[Checkpoint summary](summary.json) · [Historical engine state](state.json) · [Completed 8-session batch](batches/2025-01-01_to_2025-01-14/) · [v2 explanation](../../docs/INTRADAY_V2.md)

Any future v2 experiment must update the state and results **only after all expected NYSE sessions finish**. Do not extrapolate this 8-session checkpoint into annualized or six-month alpha.

[Dataset caveats](../../docs/DATA_QUALITY.md).
