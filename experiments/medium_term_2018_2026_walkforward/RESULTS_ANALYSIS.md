# S-04 Research diagnostics · policy-selection risk and corporate-action sensitivity

[← S-04 specification](README.md) · [Verified result report](results/README.md) · [Machine summary](results/proxy/summary.json)

> [!CAUTION]
> These are **historical price-only proxy simulations** using retrospectively assembled market data. We have **not** verified as-published financials, business competitor multiples, material-negative-news coverage, or actual settlement proceeds. Four static policies and one adaptive policy share the same broad test window, but their **unverified zero-recovery events differ** and can dominate comparison.

## 01 / Performance summary

| Variant | Ending NAV | Return | Max drawdown | Unverified $0 recovery events |
|:--|--:|--:|--:|--:|
| Defensive · fixed | $75,163.10 | -24.84% | -33.38% | 7 |
| Balanced · fixed | $76,633.03 | -23.37% | -35.78% | 10 |
| Trend bias · fixed | $61,484.35 | -38.52% | -48.04% | 8 |
| Reversal bias · fixed | **$119,808.65** | **+19.81%** | **-14.98%** | **0** |
| **Adaptive entry-policy switching** | $99,216.93 | -0.78% | -27.86% | 5 |
| SPY · continuously invested | ~ $318,979 | +218.98% | Not computed | Not applicable |

All model accounts start with $100,000 and follow the same 2018-01-02 through 2026-06-30 horizon, transaction-cost model and universal exit schedule; policy-specific entries and exposures differ. Note: **the fixed reversal policy has zero non-executable write-offs**, whereas the adaptive and other policies have 5–10. Do not read the 20.59 percentage-point gap between the adaptive and fixed reversal variants as a clean estimate of selection-method harm without reconciling corporate-action payouts and controlling exposure.

## 02 / Sequential revision chronology

| Effective date | Training cutoff | Selected profile | Phase |
|:--|:--|:--|:--|
| 2018-01-02 | Before 2018 | Balanced | Development, no history-based selection yet |
| 2019-01-02 | 2018-12-31 | Balanced | First forward-selected half-year |
| 2019-07-01 | 2019-06-28 | Reversal bias | Revised after observing 2019H1 |
| 2020-01-02 | 2019-12-31 | Reversal bias | Annual revision |
| 2021-01-04 | 2020-12-31 | Defensive | Annual revision |
| 2022-01-03 | 2021-12-31 | Reversal bias | Annual revision |
| 2023-01-03 | 2022-12-30 | Reversal bias | Annual revision |
| 2024-01-02 | 2023-12-29 | Reversal bias | Annual revision |
| 2025-01-02 | 2024-12-31 | Reversal bias | Final entry-policy review |
| 2026-01-01 onward | No new entries | Liquidation only | Fixed existing exit rules, terminal cash |

Every historical profile score is computed using **only the last 252 equity observations strictly before the effective date**. At the beginning of 2019, only 2018 development equity can rank profiles; at July 2019, only data through 2019-06-28 are available. Individual order records include both the trade date and the prior signal date, as well as close, score, five-session stock/SPY returns, and RSI for purchases.

**Important scientific limitation:** All candidate rules and the rule-ranking score were specified in 2026. A reproducible walk-forward playback with correctly lagged data is **not** automatically an untouched or prospective 2019–2025 model study. The results here support engineering correctness, not a verified ex-ante investment strategy.

## 03 / Key failure modes

### Corporate-action event handling is economically uncertain

Five positions lacked a verified executable next-open or audited cash/stock acquisition consideration. The default simulation is a conservative **zero-recovery write-off** (not a sale):

| Ticker | Written off | Approx. entry capital |
|:--|:--|--:|
| MON-201806 | 2018-06-20 | $1,035.37 |
| FOX-201903 | 2019-04-02 | $7,660.63 |
| FOXA-201903 | 2019-04-02 | $8,125.02 |
| RHT | 2019-07-22 | $10,393.64 |
| TIF | 2021-01-21 | $9,865.02 |
| **Total** | | **$37,079.68** |

These are *original invested amounts* that the model treats as unrecovered at the flagged date—not observed actual losses or measured liquidation payouts. Because removed capital can affect all subsequent investment sizing, **adding $37,079.68 back to the final NAV would not constitute a valid corrected backtest**. Re-run after independently verified event consideration and adjusted-share conversions are available.

### Slow, asymmetric reaction to losing trend or reversal setups

Of 301 executed sells, **152** were triggered by the +10% close-of-day target, **114** by the -8% initial-stop trigger, **26** by the -12% trailing-close trigger, and **9** at six months. **52.82% executed-sell win rate** did not translate into broad benchmark outperformance. A stop signal can fill materially worse at the next open during a gap.

### Lower exposure changes benchmark interpretation

The adaptive account was invested around **44.25% of NAV on average through 2025**, versus SPY buy-and-hold's full exposure. Therefore its poor relative return should be evaluated alongside unused-cash drag and market beta, not just raw return.

### Annual selector favors recent winners

Choosing the best risk-adjusted recent shadow policy can select a strategy immediately before market conditions shift. Here the adaptive return is negative while the fixed reversal profile is positive. However, this observation is **post hoc** and affected by differing corporate-action events. It is not a license to select reversal as a new 2020 start policy with hindsight.

## 04 / 2019 split and 2026 liquidation audit

**2018 development:** +6.77%. **2019H1:** -3.52%. After the documented July 2019 profile update, **2019H2:** -8.83%. Through **2020–2025** the continuing account gained **+0.07%**, but its 2020 initial equity was $93,911.97, not a fresh $100,000. During **2026H1**, the portfolio made zero new buys and gained **+5.57%** while its remaining positions were closed at simulated open fills; the last executable SELL occurred on **2026-02-17**. Ending cash and NAV both equal **$99,216.93**. Five older non-executable write-offs are *not* evidence of executed sales.

## 05 / Before claiming validated financial alpha

1. **Reconcile every historical corporate action** (cash, stock conversion ratios, distributions and dates) and rerun the full sequential book.
2. **Acquire genuinely as-published financial data** with filing release time, historical shares/EV, sector and business competitor classifications; rerun strict fail-closed mode.
3. **Document contemporaneous material adverse event/news coverage** for each reversal candidate. A price decline alone cannot establish that a negative catalyst was absent.
4. **Split model choice from evaluation:** pre-register profiles and the scoring rule for a future period never used to select them.
5. **Sensitivity analysis:** costs, fill latency, max exposure, risk-adjusted SPY and cash benchmark, stock halts, gap/slippage, and sector concentration.
6. **Compare equal conditions:** annual strategy returns, 2019H1 test and 2026 liquidation are different slices, not separately initialized portfolios.

## 06 / Reproduction & audit references

[Workflow](../../.github/workflows/swing-2018-2026-walkforward.yml) · [Trade and prior-signal audit](results/proxy/trades.csv) · [All daily NAVs](results/proxy/equity_curve.csv) · [Fixed-profile shadow NAVs](results/proxy/shadow_equity_curve.csv) · [Fixed-profile metrics](results/proxy/shadow_comparison.json) · [Dated profile selections](results/proxy/policy_log.json) · [Data manifests and checksums](results/proxy/summary.json)

[← Complete S-04 results](results/README.md)
