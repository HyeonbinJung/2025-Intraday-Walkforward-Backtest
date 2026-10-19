# Postmortem — 2025H1 One-Minute Intraday Replay

## Verified results
Initial $100,000; final $40,809.57; P&L -$59,190.43 (-59.19%). 122 NYSE sessions, 31,241 fills (256.07 per session), estimated commission and slippage $48,052.35 (48.05% of initial capital). These are historical simulated fills, not live returns. Cost is 81.18% of the *magnitude* of the loss, but this does not establish a causal cost-only counterfactual.

## Code-grounded failure hypotheses
1. **Excess turnover (high confidence):** every minute the algorithm ranks eligible tickers and targets up to five positions; deselected holdings receive sell targets, and new selections receive buy targets. No minimum hold, no rebalance hysteresis, no daily turnover budget. Fixed 5bp slippage per side plus $0.005/share commission compounds across 31,241 fills.
2. **No net-of-cost entry hurdle (high confidence):** scoring uses 5m/20m returns, relative volume, volatility, but does not estimate the prospective expected return net of spread, slippage, fees and impact before sending orders. The momentum threshold is not a calibrated net-alpha estimate.
3. **Loss adaptation is too narrow (high confidence):** on losing sell *fills*, risk shrinks to a 3% floor and momentum hurdle increases; neither the strategy family nor turnover is changed. Partial sell fills count as separate losses and may accelerate the loss streak. Repeated profitable partial fills can likewise lower it.
4. **Momentum chasing and regime mismatch (hypothesis):** positive short-term momentum plus relative volume may buy after short-lived spikes and be vulnerable to reversal, especially in volatile/down markets. Requires signal-level forward-return attribution to establish.
5. **Execution realism/data bias (high confidence as a limitation, not measured P&L cause):** next-minute OHLCV-open fills assume availability at modeled price, use 1% of *previous* minute volume, fixed slippage, and historical vendor universe that may have corporate-action/survivorship bias. Live bid/ask spreads, order queue, halts and market impact are not modeled.

## Prioritized next experiments
- Freeze the existing baseline and reproduce the $40,809.57 result without modifying its trades.
- Attribution: per month and symbol, gross vs net P&L, costs by side and ticker, number of round trips, average holding duration, turnover, return by score decile, signal-to-fill delay, and worst days.
- Ablate one factor at a time: minimum hold 5/10/20 minutes, selection hysteresis (replace only when challenger significantly better), 10/30/60-minute rebalance frequency, maximum daily turnover/trades, trade-only-if-expected-net-edge-positive, volatility/market-regime filter, stop/cooldown logic, and fee/slippage sensitivity.
- Correct loss-streak counting to completed position round trips, not partial sell fills, and add unit tests.
- Separate parameter tuning from evaluation: walk-forward train/validation/test with purging and embargo as appropriate. Never select rules based on future-period returns.
- Compare to buy-and-hold SPY, cash, and a low-turnover momentum baseline with identical trading-cost assumptions.
- Report uncertainty and robustness; do not promise positive returns.

## Copy-paste prompt for next iteration

> Work in HyeonbinJung/2025-Intraday-Walkforward-Backtest. Keep the current 2025H1 results and baseline strategy immutable. First diagnose the -59.19% return with reproducible per-month and per-ticker gross/net P&L attribution, 31,241 fill turnover, holding-time distribution, transaction cost breakdown, and loss-streak events. Verify data quality and no look-ahead. Build a separate v2 branch and implement minimum holding periods, ranking hysteresis, max daily turnover, net-of-cost expected-edge gate, completed-round-trip loss counting, and regime filtering as independently configurable ablations. Use time-ordered walk-forward training/validation/testing with strict out-of-sample evaluation, realistic spreads/slippage/fees, participation limits, and benchmarks. Run each experiment with deterministic configs, save CSV/JSON results and an experiment comparison Markdown report. Commit checkpoints to GitHub, including tests. Do not optimize on the final holdout, do not overwrite baseline, and do not claim a profitable strategy unless out-of-sample results support it. Explicitly report failures, uncertainties, drawdowns, costs, and the best risk-adjusted configuration, not just the highest return.
