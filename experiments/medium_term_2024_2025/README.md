# 2024–2025 daily medium-term S&P 500 strategy

Independent from the existing 2025 intraday backtest. Initial capital **USD 100,000**, 2024-01-02 to 2025-12-31, max **4 calendar months per position**. No hindsight: signals formed after close, trades filled at next open. 6 basis points transaction cost **per side** (1bp commission + 5bp slippage), no leverage, no interest on cash. Hold max 10 names, 12% initial equity allocation/name, 90% gross exposure (60% if SPY below 200-day moving average).

## Crucial honesty about the two backtest modes

- **proxy (executed by CI):** Select 100 *highest 63-day average dollar-volume* names from actual preceding-year December S&P 500 members. Rerank from **2023-12** for 2024 and **2024-12** for 2025. This is a liquidity proxy, **NOT the top 100 market caps**. Historical fundamentals/valuations and no-bad-news are NOT verified. The proxy run is a technical study only.
- **full (needs data):** The required two external, timestamped files must describe the **actual historical top 100 market caps** and point-in-time multiples available at each historical signal date. Without this evidence full mode fails closed. The dataset cannot establish that a 10% fall had literally 'no reason'; actual news/earnings/event investigation remains necessary in either mode.

## Fixed entry strategy

1. Sell-off proxy: five-session drop of at least **10%**, seven percentage points worse than SPY, SPY five-session drop smaller than 4%, prior session open gap better than -6%; then RSI14 under 48, positive daily close and >=2% rebound from three-session low, adjusted close >90% 200-day SMA.
2. Technical trend alternative: price > SMA20 > SMA50 > SMA200, RSI14 in 48–68, within 6% of 63-session high.
3. Mandatory liquidity/risk filters: adjusted close >$5, trailing 63-day dollar volume >=$20m, annualized trailing 63-day daily volatility <=65%.
4. Full-mode historical value screen (as-published date at least two calendar days prior to signal): at least two known valuation fields AND at least two meet: positive PE <=30, positive EV/EBITDA <=18, FCF yield >=3.5%; leverage <=3x if provided, revenue growth >=-10% if provided, operating margin positive if provided. Full-mode needs value condition **AND** either sell-off reversal or confirmed trend.

## Fixed exit strategy

On previous close, sell following open if -8% vs purchase, -12% from highest close, closing price <97% SMA50 with a negative session, +20% gain AND RSI>72, no longer in S&P 500, or first available session on/after purchase + **4 calendar months**. No trading on explicitly flagged non-trade days. Close-to-next-open stop can execute below the specified loss due to market gaps. Positions still open on 2025-12-31 are marked to market rather than fictional forced fills. No optimizing 2024–25 parameters after results are known.

## Point-in-time inputs (required for full mode)

- input/top100_pit.csv: **year,ticker,rank,asof_date**; 100 unique ranks/names per 2024 and 2025, ranking date before corresponding year. Document historic capitalization provenance; the S&P 100 index is not synonymous with the largest 100 by market cap.
- input/valuation_pit.csv: **ticker,published_at,pe_ttm,ev_ebitda,fcf_yield,net_debt_ebitda,revenue_growth,operating_margin**. Compute with historic share counts/filings, not 2026 values. Unavailable data must stay missing. Sector comparison and special bank valuation conventions remain future refinements.

## Usage

From repository root, install the dependencies from experiments/medium_term_2024_2025/requirements.txt. Then execute:

    python experiments/medium_term_2024_2025/backtest.py --mode proxy

For fully sourced market-cap/valuation data use:

    python experiments/medium_term_2024_2025/backtest.py --mode full --top100 PATH --fundamentals PATH --out PATH

CI workflow: .github/workflows/medium-term-2024-2025.yml. It runs **real 2024–25 daily adjusted market prices** and commits results/proxy/{summary.json,summary.md,equity_curve.csv,trades.csv,monthly.csv} if successful. No fabricated performance if run fails.

## Data and limitations

Prices and time-stamped S&P 500 membership: [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data), release named data. The source author describes corporate-action corrections, a post-2025 data vintage, and verification caveats. Price fields from mixed vendors are turned into synthetic split/dividend-adjusted opens using daily adjusted close/raw close ratio. Data downloaded ~236MB initially. Historical trading status from no_trade_days.csv is blocked. Adjusted total return and synthetic share-unit calculations are an approximation; validate against independent split/dividend sources. Tax, market impact beyond 5bp, delisting settlements, share availability, earnings release blackout, full news causality and volatility/beta matching are not modeled. SPY is a simple buy/hold benchmark with no modeled commissions. Proxy performance cannot be reported as the full requested fundamental strategy.
