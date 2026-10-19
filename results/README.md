# Intraday experiment outputs

[← Project home](../README.md) · [Full results overview](../docs/RESULTS.md)

| Experiment | Code | Requested period | Verified state | Latest published account |
|:--|:--|:--|:--|--:|
| **I-01 / Baseline** | [src/](../src/) | Jan–Jun 2025 | **COMPLETE** · 122 / 122 NYSE sessions | **$40,809.57** (June 30) |
| **I-02 / Lower-turnover v2** | [experiments/v2_2025H1/](../experiments/v2_2025H1/) | Jan–Jun 2025 | **PARTIAL** · 8 / 122 NYSE sessions | $97,551.06 (**Jan 14 checkpoint**) |

The original 1-minute simulation ended **-59.19%**, with approximately $48,052 in modeled trading costs; [read the postmortem](2025H1/POSTMORTEM_AND_V2_PROMPT.md). The v2 checkpoint **must not** be treated as a June 30 NAV or a six-month net return.

### Navigate to the output files

[Original complete result](2025H1/README.md) · [Original monthly account values](2025H1/MONTHLY_REPORT.md) · [v2 partial status](2025H1_v2/README.md)

Intraday `batches/*` folders preserve the detailed replay snapshots and should **not** be rearranged, because checkpoint and replay audit logic depend on their exact names.
