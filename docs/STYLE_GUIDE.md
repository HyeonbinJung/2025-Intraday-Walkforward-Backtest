# Documentation and reporting standards

[← Research documentation](README.md)

This repository follows a repeatable, GitHub-native research reporting format. Every experiment page should use **the same hierarchy and terminology** so it can be reviewed as an audit trail rather than marketing material.

## Required experiment README sections

1. **Title and navigation:** descriptive experiment name, links back to the catalog and scorecard.
2. **Research question:** exactly one research goal and its benchmark.
3. **Experimental design:** test dates, signal/data frequency, candidate universe, initial capital, fill timing, costs, exposure constraints, maximum hold.
4. **Rules:** entry branches, filters, risk sizing and liquidation conditions; clarify whether fundamental/news data is truly measured.
5. **Results:** verified status and a concise numerical table, with a direct link to the immutable-ish committed summary JSON and trade CSV.
6. **Interpretation:** describe differences **without** cherry-picking a higher result and without claiming causality.
7. **Limitations:** concrete data/source/settlement/look-ahead uncertainty; flag partial runs.
8. **Reproduction:** copyable shell commands and output-file schema.

## Required result page sections

`Status / Snapshot` → `Headline metrics` → `Period breakdown` → `Trade diagnostics` → `Raw files` → `Evidence and caveats`.

| Field | Convention |
|:--|:--|
| Currency | USD, with dollar sign and commas; **two decimals** for account NAV |
| Returns / MDD | **%**; display to two decimals, retain full JSON precision |
| Sharpe | dimensionless; **do not** call risk-free 0% Sharpe a benchmark-adjusted measure |
| Annualized performance | explicitly label CAGR vs arithmetic annualized return |
| Relative result | label percentage points (**pp**) separately from % return |
| Universe | spell out *dollar-volume top 100*, *market-cap top 100*, or *historical S&P 500 members*; these are not interchangeable |
| Trading cadence | minute or daily, with known signal time and **later** execution time |
| Status | `COMPLETE`, `PARTIAL`, or `NOT RUN`, grounded in summary JSON |
| Backtest variant | `original` or `route_aware (post-hoc)`, never silently combine |
| Benchmark | SPY total-return adjusted data with the **matched** sample period |
| Unverified assumptions | directly beside the results; no footnote-only disclosure |

Use headings consistently (`##`, `###`) and human-readable names. Keep tables short enough to scan on GitHub. Use relative repository links so navigation works from a clone or branch.

## Data preservation

- Keep `summary.json` and `trades.csv` untouched. These are the auditable inputs to any presentation.
- Put editorial analysis in `README.md` / `RESULTS_ANALYSIS.md` or `RESULTS_COMPARISON.md`, not in generated CSVs.
- Original simulation outputs remain available even after a strategy revision.
- Rerunning the simulator may regenerate `summary.md`: use the curated result README for the stable, carefully interpreted explanation.
- Do not represent a synthetic last-close merger settlement as an executed trade, or missing interim data as a 0% return.
- Do not claim that dollar-volume leaders are market-cap leaders, or that price action proves absence of negative news.

## Review checklist

- [ ] Dates and sample counts match machine-readable results.
- [ ] Initial and closing NAV reconcile with the cumulative return.
- [ ] Independent versions have independent labels and their own raw links.
- [ ] Benchmark is the **same window**.
- [ ] Every generated or editorial statement can be checked from source data.
- [ ] All navigation links resolve from their containing directory.
- [ ] Partial checkpoints have no invented completed-period metrics.
- [ ] No traded portfolio is called 'live' or 'out of sample' without evidence.
